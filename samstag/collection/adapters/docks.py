"""Official Docks event pages."""

from agenda import fold
from bar_adapters import base_event
from venue_adapters import dotted_day, clock, metadata, set_start, text


def parse_docks(soup, url):
    event = base_event(text(soup, "h1"), url, url)
    event.update(location="Les Docks", municipality="Lausanne", event_kind="MusicEvent",
                 category="Musique", source_event_key=url, adapter="docks-v1")
    day = dotted_day(text(soup, ".event-info-date"))
    if day:
        event["date"] = day.isoformat()
    for node in soup.select(".event-info-door"):
        label = text(node, ".event-info-label")
        value = node.get_text(" ", strip=True).removeprefix(label).strip()
        hour = clock(value)
        if fold(label) == "debut":
            set_start(event, day, hour)
        elif fold(label) == "portes" and hour:
            event["doors_time"] = hour.strftime("%H:%M")
    # Read the artist's prose, excluding recommendations and ticketing copy.
    prose = [n.get_text(" ", strip=True) for n in soup.select(".event-container .artist-content .the-content p")]
    event["description"] = "\n\n".join(filter(None, prose)) or metadata(soup, "og:description")[:400]
    event["image"] = metadata(soup, "og:image")
    # Inspect event header labels only, never recommended events in the footer.
    header = soup.select_one(".event-info-date")
    if header:
        ticketing = soup.select_one(".event-infos-and-ticketing")
        labels = (ticketing or header.parent).get_text(" ", strip=True)
        if "annule" in fold(labels):
            event["event_status"] = "EventCancelled"
        if "complet" in fold(labels):
            event["availability"] = "sold_out"
    if not event["title"]:
        raise ValueError("Titre du concert Docks absent")
    return event
