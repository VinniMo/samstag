"""Public programmes inspected in October 2026; incomplete facts stay in review."""
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import fold, TZ
from bar_adapters import base_event
from collection_result import CollectionResult
from config import config
from venue_adapters import set_start, dotted_day, clock


VIDY_ROOMS = {'Salle 17, Le Pavillon', 'Salle 64, Charles Apothéloz',
              'Salle 76, La Passerelle', 'Salle 96, René Gonzalez',
              'Salle 23, Studio de répétition', 'Salle René Gonzalez',
              'Foyer du théâtre', 'Théâtre de Vidy', 'Théâtre Vidy-Lausanne'}


def vidy_kind(title, genres):
    # A theatre tag can describe a discussion about a play; dance can describe
    # a workshop. These are not performances in the selected agenda.
    if (genres & {'atelier', 'workshop', 'rencontre', 'podcast', 'exposition', 'lecture', 'visite guidee'}
            or re.match(r'^(rencontre|introduction|visite|atelier|presentation|les chouettes garderies)\b', fold(title))):
        return '', 'Culture'
    for names, kind, category in [({'film','cinema'}, 'ScreeningEvent', 'Cinéma'),
                                  ({'theatre'}, 'TheaterEvent', 'Théâtre'),
                                  ({'danse'}, 'DanceEvent', 'Danse'),
                                  ({'musique','concert','opera'}, 'MusicEvent', 'Musique'),
                                  ({'humour'}, 'ComedyEvent', 'Humour')]:
        if genres & names:
            return kind, category
    return '', 'Culture'


def vidy_blocks(soup):
    node = soup.select_one('script#__NEXT_DATA__')
    if not node:
        raise ValueError('Fiche officielle Vidy sans données publiques')
    data = json.loads(node.get_text())['props']['pageProps']['node']
    blocks = json.loads(data['blocksJSON'])
    def walk(rows):
        for row in rows:
            yield row
            yield from walk(row.get('innerBlocks') or [])
    return list(walk(blocks))


def confirm_vidy(result, fetch, now=None):
    from scraper import FetchError
    now = now or datetime.now(TZ)
    eligible = []
    for event in result.events:
        event['detail_confirmed'] = False
        try:
            start = datetime.fromisoformat(event['start_at'])
        except (KeyError, ValueError):
            continue
        if (event.get('event_kind') and event.get('room') in VIDY_ROOMS
                and event.get('time_role') != 'unverified' and start.hour >= 17
                and now <= start <= now + timedelta(days=config.COLLECTION_HORIZON_DAYS)):
            eligible.append(event)
    targets = list(dict.fromkeys(e['url'] for e in eligible))
    failures = 0
    for target in targets[:config.MAX_DETAIL_PAGES]:
        try:
            if (urlparse(target).hostname or '').removeprefix('www.') != 'vidy.ch':
                raise ValueError('Lien de fiche hors du site officiel Vidy')
            blocks = vidy_blocks(BeautifulSoup(fetch(target), 'lxml'))
            metas = [b['attributes'] for b in blocks if b.get('name') == 'supt/header-metas']
            if len(metas) != 1:
                raise ValueError('Métadonnées de spectacle ambiguës')
            meta = metas[0]
            genres = {fold(g.get('title', '')) for g in meta.get('genres') or []}
            sessions = [row for b in blocks if b.get('name') == 'supt/section-dates-times'
                        for row in (b.get('attributes') or {}).get('rows', [])]
            # Some single screenings publish the session only in the header,
            # rather than duplicating it in the ticket schedule section.
            if not sessions:
                from expanded_adapters import french_day
                label = BeautifulSoup(meta.get('dates') or '', 'lxml').get_text(' ', strip=True)
                match = re.fullmatch(r'Le\s+(\d{1,2}(?:er)?\s+\w+\s+\d{4})\s*•\s*(\d{1,2}:\d{2})', label, re.I)
                day = french_day(match[1]) if match else None
                hour = clock(match[2]) if match else None
                if day and hour:
                    sessions = [{'date':datetime.combine(day,hour).strftime('%Y-%m-%d %H:%M:%S'),
                                 'location':meta.get('location')}]
            if not sessions:
                raise ValueError('Fiche sans séances explicites')
            for event in (e for e in eligible if e['url'] == target):
                expected = datetime.fromisoformat(event['start_at']).strftime('%Y-%m-%d %H:%M:%S')
                matches = [s for s in sessions if s.get('date') == expected and s.get('location') == event['room']]
                if len(matches) != 1:
                    event['schedule_conflict'] = True
                    continue
                event['event_kind'], event['category'] = vidy_kind(event['title'], genres)
                state = (matches[0].get('state') or '').upper()
                if state in {'CANCELLED', 'CANCELED'}:
                    event['event_status'] = 'EventCancelled'
                elif state == 'POSTPONED':
                    event['event_status'] = 'EventPostponed'
                elif state and state not in {'ON_SALE', 'RUNNING', 'PREPARING', 'VALIDATED'}:
                    event['event_status'] = 'unverified'
                event.update(detail_confirmed=True, evidence_url=target)
        except (ValueError, TypeError, KeyError, OSError, RuntimeError, FetchError):
            failures += 1
    result.method = f'vidy-public-calendar-v2: {min(len(targets), config.MAX_DETAIL_PAGES)}/{len(targets)} fiches, {failures} erreurs ; séances recoupées (sélection publiée)'
    return result


def parse_vidy(soup, url):
    node = soup.select_one('script#__NEXT_DATA__')
    if not node:
        raise ValueError('Calendrier public Vidy absent')
    data = json.loads(node.get_text())['props']['pageProps']['node']
    rows = (data.get('archive') or {}).get('eventDates')
    if not data.get('isCalendarPage') or not isinstance(rows, list):
        raise ValueError('Structure du calendrier Vidy modifiée')
    events = []
    for row in rows:
        show = row['event']
        target = urljoin(url, show.get('link') or url)
        event = base_event(unescape_title(show['title']), target, url)
        room = (row.get('location') or {}).get('name', '')
        event.update(location='Théâtre Vidy-Lausanne' if room in VIDY_ROOMS else room,
                     municipality='Lausanne' if room in VIDY_ROOMS else '', room=room,
                     source_event_key=f"vidy:{show['id']}:{row.get('date')}:{room}",
                     adapter='vidy-public-calendar-v2')
        genres = {fold((g.get('translation') or {}).get('name', ''))
                  for g in (show.get('genres') or {}).get('nodes', [])}
        event['event_kind'], event['category'] = vidy_kind(event['title'], genres)
        # A calendar date is a performance, not the entire show's date range.
        try:
            start = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
            set_start(event, start.date(), start.time())
            if start.hour == start.minute == 0:
                event['time_role'] = 'unverified'  # all-day marker, not midnight
        except (ValueError, TypeError, KeyError):
            pass
        state = row.get('state')
        if state in {'CANCELED', 'CANCELLED'}:
            event['event_status'] = 'EventCancelled'
        elif state == 'POSTPONED':
            event['event_status'] = 'EventPostponed'
        elif state not in {'ON_SALE','RUNNING','PREPARING','VALIDATED'}:
            event['event_status'] = 'unverified'
        event['description'] = BeautifulSoup(show.get('excerpt') or '', 'lxml').get_text(' ', strip=True)[:400]
        image = ((show.get('image') or {}).get('node') or {}).get('src')
        event['image'] = urljoin(url, image) if image else ''
        events.append(event)
    # The site supplies a selection of calendar dates, with no completeness
    # contract. Absence from this list must never withdraw a previous event.
    return CollectionResult(events, 'vidy-public-calendar-v1 (sélection publiée)', partial=True)


def unescape_title(value):
    from html import unescape
    return unescape(value).strip()


def collect_programme(url, soup, fetch):
    host = (urlparse(url).hostname or '').removeprefix('www.')
    if host == 'app.hango.ch' and urlparse(url).path.startswith('/venues/'):
        # Follow only public event cards on the configured venue page. This
        # reader uses no widget key or private endpoint.
        from scraper import _normalize_jsonld, _jsonld_items, _is_event
        targets = list(dict.fromkeys(urljoin(url, a['href']) for a in soup.select('a[href]')
                                     if re.fullmatch(r'/events/[^/]+', urlparse(a['href']).path)
                                     and urlparse(urljoin(url, a['href'])).hostname == host))
        events, failures = [], 0
        for target in targets[:config.MAX_DETAIL_PAGES]:
            try:
                detail = BeautifulSoup(fetch(target), 'lxml')
                rows = []
                for script in detail.select('script[type="application/ld+json"]'):
                    for structured in _jsonld_items(json.loads(script.get_text())):
                        if not _is_event(structured):
                            continue
                        location = structured.get('location') or {}
                        # A venue page can show related recommendations. Only
                        # the exact configured public venue identity qualifies.
                        if not isinstance(location, dict) or (location.get('@id') or '').rstrip('/') != url.rstrip('/'):
                            failures += 1
                            continue
                        event = _normalize_jsonld(structured, target)
                        if not event:
                            continue
                        event['source_event_key'] = target
                        keywords = {fold(k.strip()) for k in structured.get('keywords', '').split(',')}
                        if 'dj set' in keywords:
                            event.update(event_kind='ClubNight', category='Clubbing')
                        rows.append(event)
                if not rows:
                    failures += 1
                events.extend(rows)
            except Exception:
                failures += 1
        return CollectionResult(events, f'hango-public-pages: {len(targets)} fiches annoncées, {failures} erreurs (sélection non exhaustive)', partial=True)
    if host == 'vidy.ch':
        if urlparse(url).path.rstrip('/') != '/fr/calendrier':
            link = soup.select_one('a[href="/fr/calendrier/"]')
            if not link:
                raise ValueError('Lien calendrier Vidy absent')
            url = urljoin(url, link['href'])
            soup = BeautifulSoup(fetch(url), 'lxml')
        return confirm_vidy(parse_vidy(soup, url), fetch)
    if host == 'bleu-lezard.ch':
        empty = soup.select_one('.jet-listing-not-found')
        if empty and 'aucun evenement' in fold(empty.get_text(' ', strip=True)):
            return CollectionResult([], 'bleu-lezard: programme officiel explicitement vide')
        # A changed listing must be inspected before interpreting its fields.
        raise ValueError('Programme Bleu Lézard non vide : structure à qualifier')
    if host == 'holymonkey.ch':
        events = []
        for heading in soup.select('p.wp-block-paragraph strong'):
            label = heading.get_text(' ', strip=True)
            if not re.match(r'^(LUNDI|MARDI|MERCREDI|JEUDI|VENDREDI|SAMEDI|DIMANCHE)\b', label):
                continue
            event = base_event(label, url, url)
            event.update(location='Holy Monkey', municipality='Lausanne',
                         description=heading.parent.get_text(' ', strip=True)[:400])
            # No published year or session time: never infer from opening hours.
            events.append(event)
        if not events:
            raise ValueError('Annonces Holy Monkey absentes ou structure modifiée')
        return CollectionResult(events, 'holy-monkey: annonces sans année ni heure, en revue', partial=True)
    if host == 'hungrybearfood.ch':
        events = []
        for heading in soup.select('h1.heading'):
            label = heading.get_text(' ', strip=True)
            event = base_event(label, url, url)
            event.update(location='Hungry Bear', municipality='Lausanne')
            match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', label)
            if match:
                day = dotted_day(match[0])
                event['date'] = day.isoformat() if day else ''
            events.append(event)
        if not events:
            raise ValueError('Annonces Hungry Bear absentes ou structure modifiée')
        return CollectionResult(events, 'hungry-bear: annonces sans heure, en revue', partial=True)
    return None
