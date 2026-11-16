"""Official La Brèche event detail pages."""

import re

from venue_adapters import clock, dotted_day, set_start, text
from agenda import fold
from .common import event_at


def parse_breche(soup, url):
    title = " + ".join(n.get_text(" ", strip=True) for n in soup.select(".artist-div-2 .h2-2") if n.get_text(strip=True))
    if not title:
        return []
    event = event_at(title, url, url, "La Brèche", "", "Culture")
    event["source_event_key"] = url
    title_text = soup.title.get_text(" ", strip=True) if soup.title else ""
    day = dotted_day(title_text)
    content = soup.get_text(" ", strip=True)
    opening = re.search(r"Portes\s*:\s*(\d{1,2}h\d{0,2})", content, re.I)
    start = re.search(r"Début\s*:\s*(\d{1,2}h\d{0,2})", content, re.I)
    if opening and clock(opening[1]):
        event["doors_time"] = clock(opening[1]).strftime("%H:%M")
    set_start(event, day, clock(start[1]) if start else None)
    # An explicit ticket URL supplies the event family; don't classify
    # every item in a multidisciplinary programme as a concert.
    if soup.select_one('a[href*="petzi.ch"]') and "a people's history" not in fold(title):
        event.update(event_kind="MusicEvent", category="Musique")
    if "halloween" in fold(title):
        event.update(event_kind="ClubNight", category="Clubbing")
    if "impro" in fold(title):
        event.update(event_kind="TheaterEvent", category="Théâtre")
    paragraphs = [n.get_text(' ', strip=True).replace('\u200d', '').strip()
                  for n in soup.select('.div-flexbox-artiste .hyphen.w-richtext p')]
    event["description"] = '\n\n'.join(p for p in paragraphs if p) or text(soup, ".rich-text-block")[:400]
    return [event]
