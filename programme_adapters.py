"""Public programmes inspected in October 2026; incomplete facts stay in review."""
import json
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import fold, TZ
from bar_adapters import base_event
from collection_result import CollectionResult
from config import config
from venue_adapters import dotted_day


# Compatibility imports during the incremental package migration.
# The implementation lives in one place; remove these after callers migrate.
from samstag.collection.adapters.vidy import (
    VIDY_ROOMS, vidy_kind, vidy_blocks, confirm_vidy, parse_vidy, unescape_title,
)


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
