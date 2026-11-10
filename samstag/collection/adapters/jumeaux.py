"""Official Jumeaux Jazz Club programme cards."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from agenda import fold
from bar_adapters import base_event
from venue_adapters import clock, dotted_day, set_start, text


def parse_jumeaux(soup, url):
    events = []
    for original in soup.select(".nextevent"):
        card = BeautifulSoup(str(original), "lxml")
        for node in card.select(".w-condition-invisible, .w-dyn-bind-empty, [hidden]"):
            node.decompose()
        title = text(card, ".event__title")
        if not title:
            continue
        link = card.select_one('a[href*="/evenements/"]')
        detail_url = urljoin(url, link["href"]) if link else url
        event = base_event(title, detail_url, url)
        event.update(location="Jumeaux Jazz Club", municipality="Lausanne", event_kind="MusicEvent",
                     category="Musique", adapter="jumeaux-v1")
        if link:
            event["source_event_key"] = detail_url
        day = dotted_day(text(card, ".concert__date"))
        if day:
            event["date"] = day.isoformat()
        for detail in card.select(".concert__detail"):
            content = detail.get_text(" ", strip=True)
            if content.startswith("Portes"):
                match = re.search(r"Concert\s+(\d{1,2}[hH:]\d{0,2})\b", content)
                set_start(event, day, clock(match[1]) if match else None)
                opening = re.search(r"Portes\s+(\d{1,2}[hH:]\d{0,2})\b", content)
                if opening:
                    hour = clock(opening[1])
                    event["doors_time"] = hour.strftime("%H:%M") if hour else ""
            elif content.startswith("Tarif normal"):
                match = re.search(r"Tarif normal\s+(\d+(?:[.,]\d+)?)\s+CHF", content)
                if match:
                    event["price"] = "CHF " + match[1]
        visible = card.get_text(" ", strip=True)
        alerts = " ".join(n.get_text(" ", strip=True) for n in card.select(".nextevent__alert"))
        if "annule" in fold(alerts):
            event["event_status"] = "EventCancelled"
        if "complet" in fold(alerts):
            event["availability"] = "sold_out"
        if any(n.get_text(" ", strip=True) == "Entrée Libre" for n in card.select(".event__number")):
            event["price"] = "Gratuit"
        event["description"] = " ".join(filter(None, [text(card, ".concert__desc"), text(card, ".concert__desc--rich"), text(card, ".event__band__style")]))[:400]
        if "stand up" in fold(visible):
            event.update(event_kind="ComedyEvent", category="Humour")
        image = card.select_one("img[src]")
        event["image"] = urljoin(url, image["src"]) if image else ""
        events.append(event)
    return events
