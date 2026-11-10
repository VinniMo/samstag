"""Official activity cards and detail pages for La Grange UNIL."""
import re
from datetime import date
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import fold
from collection_result import CollectionResult
from config import config
from venue_adapters import clock, dotted_day, set_start, text

from .common import event_at


def collect_grange(soup, url, fetch):
    events = []
    programme = soup.select_one('a[href*="/recherche-dactivites/"]')
    if programme and urlparse(url).path.rstrip('/') != '/recherche-dactivites':
        target = urljoin(url, programme['href'])
        if (urlparse(target).hostname or '').removeprefix('www.') == 'grange-unil.ch':
            soup = BeautifulSoup(fetch(target), 'lxml')
    cards = soup.select('a.card[href]')
    checked, failed, unread = 0, 0, 0
    targets = set()
    for card in cards[:config.MAX_DETAIL_PAGES]:
        title = text(card, '.event-card-title')
        genres = fold(text(card, '.list-inline'))
        if not title or not any(w in genres for w in ['danse','theatre','performance','musique']):
            continue
        kind, category = (('DanceEvent','Danse') if 'danse' in genres else
                          ('MusicEvent','Musique') if 'musique' in genres else ('TheaterEvent','Théâtre'))
        # Workshops remain outside the admitted event types.
        if 'atelier' in genres:
            continue
        days = [dotted_day(value) for value in re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', text(card,'.card-footer'))]
        if not days or any(d is None for d in days):
            continue
        target = urljoin(url, card['href'])
        if (urlparse(target).hostname or '').removeprefix('www.') != 'grange-unil.ch':
            continue
        if target in targets:
            continue
        targets.add(target)
        checked += 1
        try:
            detail = BeautifulSoup(fetch(target),'lxml')
            panels = detail.select('.event-right-content')
            seen = set()
            before = len(events)
            for panel in panels:
                # Venue and session times are sibling blocks within the same
                # sidebar. Never borrow a location from the page footer.
                if not any(re.fullmatch(r'>\s*La\s+Grange', p.get_text(' ', strip=True)) for p in panel.select('p')):
                    continue
                for line in panel.select('p'):
                    match = re.match(r'^(Lu|Ma|Me|Je|Ve|Sa|Di)\s+(\d{1,2})\.(\d{1,2}),\s*(\d{1,2}h\d{0,2})\b',line.get_text(' ',strip=True))
                    if not match:
                        continue
                    possibilities = []
                    for year in range(min(days).year, max(days).year+1):
                        try:
                            day = date(year,int(match[3]),int(match[2]))
                            if min(days) <= day <= max(days):
                                possibilities.append(day)
                        except ValueError:
                            continue
                    if len(possibilities) != 1:
                        continue
                    day = possibilities[0]
                    key = (day,match[4])
                    if key in seen:
                        continue
                    seen.add(key)
                    event = event_at(title,target,target,'La Grange UNIL',kind,category)
                    from source_registry import VENUES
                    venue = next(v for v in VENUES if v['id'] == 'L029')
                    event['municipality'] = venue['commune']
                    event['municipality_proof'] = venue.get('preuve_commune', '')
                    set_start(event,day,clock(match[4]))
                    events.append(event)
            if len(events) == before:
                unread += 1
        except Exception:
            failed += 1
    if not checked:
        raise ValueError('Aucune fiche de spectacle datée trouvée à La Grange')
    return CollectionResult(events,f'grange-programme-v3: {checked} fiches, {failed} erreurs, {unread} sans séance lisible',partial=bool(failed or unread or len(cards) > config.MAX_DETAIL_PAGES))
