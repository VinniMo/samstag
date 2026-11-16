"""Official Cinéma Oblò programme cards."""

import re
from datetime import date
from urllib.parse import urljoin, urlparse

from venue_adapters import clock, set_start
from agenda import fold
from .common import event_at


def parse_oblo(soup, url):
    events = []
    for card in soup.select('a[href^="/events/"]'):
        target = urljoin(url, card["href"])
        match = re.fullmatch(r"/events/(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})/?", urlparse(target).path)
        spans = [n.get_text(" ", strip=True) for n in card.select("span")]
        if not match or len(spans) != 5:
            continue
        title, genres = spans[3], fold(spans[4])
        kind = "ScreeningEvent" if any(w in genres for w in ["metrage", "documentaire", "cinema"]) else "TheaterEvent" if "performances" in genres else ""
        event = event_at(title, target, url, "Cinéma Oblò", kind, "Cinéma" if kind == "ScreeningEvent" else "Théâtre" if kind else "Culture")
        day = date.fromisoformat(match[1])
        hour = clock(match[2]+":"+match[3])
        visible = clock(spans[2])
        # Cross-check encoded time with the actual programme label.
        if hour == visible and str(day.day) == re.sub(r"^0", "", spans[1].split()[0]):
            set_start(event, day, hour)
        event.update(description=spans[4], source_event_key=target)
        events.append(event)
    if not events:
        raise ValueError("Programme Oblò absent ou structure modifiée")
    return events
