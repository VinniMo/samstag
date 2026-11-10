"""Lausanne Tourisme detail pages used as aggregator evidence."""

import json
import re
from datetime import datetime, time, timedelta

from agenda import TZ, fold

from .bars import base_event
from venue_adapters import clock, dotted_day, metadata, set_start, text


def parse_tourisme(soup, url):
    title = text(soup, "h1.hero__title")
    if not title:
        return None
    event = base_event(title, url, url)
    event.update(location=text(soup, ".gmtLocationSingle"), adapter="lausanne-tourisme-v1", source_event_key=url)
    event["description"] = text(soup, ".hero__content")[:400]
    event["image"] = metadata(soup, "og:image")
    price = soup.select_one(".hero__price span")
    event["price"] = price.get_text(" ", strip=True) if price else ""
    tags = fold(text(soup, ".hero__tags"))
    kinds = {"musique": ("MusicEvent", "Musique"), "theatre": ("TheaterEvent", "Théâtre"),
             "cinema": ("ScreeningEvent", "Cinéma"), "danse": ("DanceEvent", "Danse"), "humour": ("ComedyEvent", "Humour")}
    if tags in kinds:
        event["event_kind"], event["category"] = kinds[tags]
    address = soup.select_one(".tabs__content-item .address")
    if address:
        for node in address.select("p"):
            node.decompose()
        event["address"] = address.get_text(", ", strip=True)
        city = re.search(r"\b\d{4}\s+([^,]+)$", event["address"])
        event["municipality"] = city[1].strip() if city else ""
    dates = text(soup, ".gmtDateSingle")
    # Only a single explicitly written day is normalized here. Weekly ranges
    # remain for review instead of manufacturing daily occurrences.
    if len(re.findall(r"\d{1,2}\.\d{1,2}\.\d{4}", dates)) == 1:
        day = dotted_day(dates)
        if day:
            event["date"] = day.isoformat()
            opening = soup.select_one(".js-openingHours[data-opening]")
            if opening:
                data = json.loads(opening["data-opening"])
                spans = data.get("openings", [])
                first = [s for s in spans if s.get("day") == day.isoweekday()]
                if len(first) == 1 and re.fullmatch(r"\d{4}", first[0].get("from", "")):
                    value = first[0]["from"]
                    set_start(event, day, clock(value[:2]+":"+value[2:]))
                    until = first[0].get("until", "")
                    if re.fullmatch(r"\d{4}", until):
                        end = datetime.combine(day, time(int(until[:2]), int(until[2:])), TZ)
                        if until == "2359":
                            following = [s for s in spans if s.get("day") == (day+timedelta(days=1)).isoweekday() and s.get("from") == "0000"]
                            if len(following) == 1 and re.fullmatch(r"\d{4}", following[0].get("until", "")):
                                value = following[0]["until"]
                                end = datetime.combine(day+timedelta(days=1), time(int(value[:2]), int(value[2:])), TZ)
                        event.update(end_at=end.isoformat(), end_date=end.date().isoformat())
    return event
