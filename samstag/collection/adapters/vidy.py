"""Official Vidy calendar and session confirmation.

The public calendar is a selection: absence never withdraws previous events.
"""
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import fold, TZ
from bar_adapters import base_event
from collection_result import CollectionResult
from config import config
from venue_adapters import set_start, clock


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
                and event.get('time_role') != 'unverified'
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
