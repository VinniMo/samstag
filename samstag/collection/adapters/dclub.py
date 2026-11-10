"""Official D! Club programme and confirmed concert starts."""

import json
import logging
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import TZ, fold
from bar_adapters import base_event
from collection_result import CollectionResult
from config import config
from venue_adapters import MONTHS, clock, set_start, text

log = logging.getLogger(__name__)


def parse_dclub(soup, url):
    events = []
    for card in soup.select(".event[data-date][data-place]"):
        places = json.loads(card["data-place"])
        styles = json.loads(card.get("data-styles") or "[]")
        main = card.select_one("a.main[href]")
        if not main:
            continue
        title = text(card, ".dtitle")
        artists = [n.get_text(" ", strip=True) for n in card.select(".header .name")]
        title = (title or ", ".join(artists)) if "concert" in styles else " — ".join(filter(None, [title, ", ".join(artists)]))
        if not title:
            continue
        detail = urljoin(url, main["href"])  # retain room fragment (#d-club / #abc)
        event = base_event(title, detail, url)
        event.update(location="D! Club" if places == ["d-club"] else "Bar Club Abc" if places == ["abc"] else "",
                     municipality="Lausanne", time_role="doors", source_event_key=detail,
                     adapter="dclub-v1", source_room=places, source_styles=styles, artists=artists)
        if styles and all(s in {"electronic", "urban", "theme"} for s in styles):
            event.update(event_kind="ClubNight", category="Clubbing")
        elif "concert" in styles:
            event.update(event_kind="MusicEvent", category="Musique")
        try:
            day = datetime.strptime(card["data-date"], "%Y%m%d").date()
            event["date"] = day.isoformat()
        except ValueError:
            day = None
        match = re.search(r"Porte:\s*(\d{1,2}:\d{2})", text(card, ".door"))
        set_start(event, day, clock(match[1]) if match else None)
        image = card.select_one("a.image img")
        if image:
            image_url = image.get("data-lazy-src") or image.get("src", "")
            event["image"] = urljoin(url, image_url) if not image_url.startswith("data:") else ""
        event["description"] = text(card, ".details")[:400]
        events.append(event)
    return events


def collect_dclub(soup, url, fetch):
    """Keep doors distinct; qualify concerts only with an explicit artistic time."""
    rows = parse_dclub(soup, url)
    partial = False
    details = 0
    today = datetime.now(TZ).date()
    for event in rows:
        if event.get("event_kind") != "MusicEvent":
            continue
        day = date.fromisoformat(event["date"]) if event.get("date") else None
        if not day or not today <= day <= today + timedelta(days=config.COLLECTION_HORIZON_DAYS):
            continue
        if details >= config.MAX_DETAIL_PAGES:
            partial = True
            continue
        details += 1
        try:
            detail_url = event["url"].split("#")[0]
            detail = BeautifulSoup(fetch(detail_url), "lxml")
            room = detail.find(id=urlparse(event["url"]).fragment)
            if not room or text(room, ".date-title") != event["title"]:
                partial = True
                continue
            description = text(room, ".dclub-date-content > div")
            event.update(description=description[:600], evidence_url=event["url"])
            if re.search(r"\bgratuit(?:e|es|s)?\b", fold(description)):
                event["price"] = "Gratuit sur inscription" if "inscription" in fold(description) else "Gratuit"
            # Only the inspected registration provider, explicitly linked by
            # this event's official detail, can supply its artistic start.
            for anchor in room.select(".action a[href]"):
                ticket = urljoin(detail_url, anchor["href"])
                if urlparse(ticket).scheme != "https" or urlparse(ticket).hostname != "visaevents.swoogo.com":
                    continue
                registration = BeautifulSoup(fetch(ticket), "lxml")
                for node in registration(["script", "style", "header", "footer"]):
                    node.decompose()
                body = fold(registration.get_text(" ", strip=True))
                # Confirm venue, exact day/month and every advertised artist.
                artists = [fold(a) for a in event.get("artists", [])]
                date_label = f"{day.day} {list(MONTHS)[day.month-1]}"
                times = set(re.findall(r"\bconcert\s*:\s*(\d{1,2}[h:]\d{2})\b", body))
                if "d! club" not in body or date_label not in body or not artists or not all(a in body for a in artists) or len(times) != 1:
                    continue
                hour = clock(next(iter(times)))
                if not hour or (event.get("time") and hour.strftime("%H:%M") < event["time"]):
                    continue
                event["doors_time"] = event.get("time", "")
                set_start(event, day, hour)
                event.update(time_role="start", artistic_time_confirmed=True,
                             start_evidence_url=ticket, ticket_url=ticket)
                if "gagnants sont tires au sort" in body:
                    event["access_conditions"] = "Inscription avec tirage au sort ; entrée sur confirmation de l’organisateur."
                break
        except Exception as exc:
            log.warning("D! concert detail failed %s: %s", event["url"], exc)
            partial = True
    return CollectionResult(rows, "dclub-official-programme-v2 (concerts confirmés, portes distinctes)", partial=partial)
