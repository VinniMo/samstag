"""Official multi-venue programme for JazzOnze+."""

import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import TZ, fold
from collection_result import CollectionResult
from config import config
from venue_adapters import clock, set_start, text

from .common import event_at, french_day


def parse_jazzonze(soup, url):
    events = []
    labels = {
        'Casino de Montbenon (Salle Paderewski et Salle des Fêtes)': ['Salle Paderewski', 'Salle des Fêtes'],
        'Jumeaux Jazz Club': ['Jumeaux Jazz Club'],
        'BCV Concert Hall': ['BCV Concert Hall'],
        'EJMA (Atrium et Auditorium)': ['Atrium de l’EJMA', 'Auditorium de l’EJMA'],
    }
    addresses = {}
    for anchor in soup.select('a[href]'):
        label = anchor.get_text(' ', strip=True)
        if label not in labels or 'google.' not in anchor['href']:
            continue
        # Keep the named access block, never the festival administration address.
        for parent in list(anchor.parents)[:3]:
            value = parent.get_text(' ', strip=True).removeprefix(label).strip()
            if re.fullmatch(r'[^\d]+\d+[^\d]*\s+1003\s+Lausanne', value):
                for venue in labels[label]:
                    addresses[venue] = value
                break
    for card in soup.select('.rfp-item'):
        title = text(card, '.rfp-item-title')
        parts = [s.strip() for s in text(card, '.program').split('/')]
        link = card.select_one('a.rfp-mask[href]')
        if not title or len(parts) != 4 or not link:
            continue
        venue = parts[1].replace("'", '’')
        event = event_at(title, urljoin(url, link['href']), url, venue, 'MusicEvent', 'Musique')
        if venue in addresses:
            event.update(address=addresses[venue], address_proof=url)
        set_start(event, french_day(parts[0]), clock(parts[2]))
        event['price'] = parts[3]
        event['source_event_key'] = event['url']
        if 'annule' in fold(title):
            event['event_status'] = 'EventCancelled'
        # Midnight is printed beneath the preceding evening date in this
        # programme; keep it for review until the ticket confirms civil date.
        if event.get('time') == '00:00':
            event['time_role'] = 'unverified'
        image = card.select_one('img[src]')
        event['image'] = image['src'] if image else ''
        events.append(event)
    if not events:
        raise ValueError('Programme JazzOnze+ absent ou structure modifiée')
    return events


def collect_jazzonze(soup, url, fetch):
    events = parse_jazzonze(soup, url)
    today = datetime.now(TZ).date()
    checked, partial = 0, False
    for event in events:
        if not event.get('date') or not today <= date.fromisoformat(event['date']) <= today + timedelta(days=config.COLLECTION_HORIZON_DAYS):
            continue
        if event.get('event_status') == 'EventCancelled' or not event.get('time'):
            continue
        if checked >= config.MAX_DETAIL_PAGES or urlparse(event['url']).hostname != urlparse(url).hostname:
            partial = True
            continue
        checked += 1
        try:
            detail = BeautifulSoup(fetch(event['url']), 'lxml')
            if fold(text(detail, 'h1.entry-title')) != fold(event['title']):
                partial = True
                continue
            paragraphs = [n.get_text(' ', strip=True) for n in detail.select('article .entry-content > p')]
            event['description'] = '\n\n'.join(p for p in paragraphs if p)
            event['description_evidence_url'] = event['url']
        except Exception:
            partial = True
    return CollectionResult(events, f'jazzonze-programme-v3: {checked} fiches contrôlées', partial=partial)
