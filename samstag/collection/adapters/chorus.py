"""Official Chorus Jazz Club programme sections."""

import re
from datetime import date
from urllib.parse import urljoin

from agenda import fold
from bar_adapters import base_event
from venue_adapters import MONTHS, clock, set_start, text


def parse_chorus(soup, url):
    events = []
    for section in soup.select("section.menu_page"):
        period = re.search(r"PROGRAMME\s+(\w+)\s+(\d{4})", fold(text(section, ".section_title")), re.I)
        if not period or period[1] not in MONTHS:
            continue
        month, year = MONTHS[period[1]], int(period[2])
        for card in section.select(".our_event_list"):
            link = card.select_one(".eventtexttitle a[href]")
            if not link:
                continue
            event = base_event(link.get_text(" ", strip=True), urljoin(url, link["href"]), url)
            event.update(location="Chorus Jazz Club", municipality="Lausanne", event_kind="MusicEvent",
                         category="Musique", adapter="chorus-v1", source_event_key=event["url"])
            match = re.match(r"(\d{1,2})\s+(\w+)", fold(text(card, ".day_month")))
            # Year and month are explicitly attached to this programme section.
            if match and period[1].startswith(match[2]):
                try:
                    set_start(event, date(year, month, int(match[1])), clock(text(card, ".event_time")))
                except ValueError:
                    pass
            event["description"] = text(card, ".event_descbx")[:400]
            price = text(card, ".event_location")
            if "entree libre" in fold(price):
                event["price"] = "Entrée libre"
            else:
                amount = re.search(r"\d+(?:[.,]\d+)?\.-", price)
                if amount:
                    event["price"] = amount[0]
            if fold(text(card, ".event_buyticket")) == "complet":
                event["availability"] = "sold_out"
            image = card.select_one(".eventthumb img[src]")
            event["image"] = urljoin(url, image["src"]) if image else ""
            events.append(event)
    return events
