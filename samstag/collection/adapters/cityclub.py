"""Official monthly screening programme for Cinéma CityClub in Pully."""
import re
from datetime import date
from urllib.parse import urljoin, urlparse

from bar_adapters import base_event
from venue_adapters import clock, set_start, text


def parse_cityclub(soup, url):
    match = re.search(r"/affiche/(\d{4})-(\d{2})-00/?$", urlparse(url).path)
    cards = soup.select(".action[data-idaction]")
    if not match or not cards:
        raise ValueError("Programme mensuel CityClub absent ou structure modifiée")
    year, month = int(match[1]), int(match[2])
    events = []
    for card in cards:
        title = text(card, "h4")
        if not title:
            continue
        for session in card.select(".projections a[href]"):
            found = re.search(r"\b(\d{1,2})\.(\d{1,2})\s*/\s*(\d{1,2}h\d{0,2})\b", session.get_text(" ", strip=True))
            if not found:
                continue
            # The monthly programme can explicitly list next-month sessions.
            session_month = int(found[2])
            if session_month not in {month, month % 12 + 1}:
                continue
            try:
                day = date(year + int(month == 12 and session_month == 1), session_month, int(found[1]))
            except ValueError:
                continue
            target = urljoin(url, session["href"])
            event = base_event(title, target, url)
            event.update(location="Cinéma CityClub", municipality="Pully",
                         event_kind="ScreeningEvent", category="Cinéma",
                         adapter="official-programme-v3")
            set_start(event, day, clock(found[3]))
            event["description"] = text(card, ".description")[:400]
            image = card.select_one("img.localVignette[src]")
            event["image"] = urljoin(url, image["src"]) if image else ""
            event["source_event_key"] = target
            events.append(event)
    return events
