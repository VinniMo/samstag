"""Official dated performance calendar for Pavillon Naftule."""
from datetime import date
from urllib.parse import urljoin

from venue_adapters import clock, set_start, text

from .common import event_at


def parse_naftule(soup, url):
    panels = soup.select("[data-day-panel][data-day]")
    if not panels:
        raise ValueError("Calendrier Naftule absent ou structure modifiée")
    events = []
    for panel in panels:
        try:
            day = date.fromisoformat(panel["data-day"])
        except ValueError:
            continue
        for card in panel.select("li[data-show]"):
            genres = set(card.get("data-genres", "").split())
            kind, category = ("ComedyEvent", "Humour") if "humour" in genres else (
                ("MusicEvent", "Musique") if "musique-et-chant" in genres else ("", "Culture"))
            title = text(card, "h3")
            if not title:
                continue
            link = card.select_one("h3 a[href]")
            target = urljoin(url, link["href"]) if link else url
            event = event_at(title, target, url, "Pavillon Naftule", kind, category)
            times = [clock(n.get_text(" ", strip=True)) for n in card.select("span")]
            hours = [t for t in times if t]
            set_start(event, day, hours[0] if len(hours) == 1 else None)
            # Ticket page is a series: each performance keeps its own identity.
            image = card.select_one("img[src]")
            event["image"] = urljoin(url, image["src"]) if image else ""
            events.append(event)
    return events
