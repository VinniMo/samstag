"""Official programme cards for Folklor."""
from urllib.parse import urljoin

from venue_adapters import clock, dotted_day, set_start, text

from .common import event_at


def parse_folklor(soup, url):
    cards = soup.select("#program article.event")
    if not cards:
        raise ValueError("Programme Folklor absent ou structure modifiée")
    events = []
    for card in cards:
        title = text(card, ".event-title")
        if not title:
            continue
        link = card.select_one(".event-artists a[href]")
        target = urljoin(url, link["href"]) if link else url
        event = event_at(title, target, url, "Folklor", "ClubNight", "Clubbing")
        set_start(event, dotted_day(text(card, ".event-date")), clock(text(card, ".event-time")))
        event["description"] = text(card, ".event-artists")[:400]
        if link:
            event["source_event_key"] = target
        events.append(event)
    return events
