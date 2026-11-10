"""Site-specific readers, based on inspected public programme pages."""
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import urlparse

from agenda import TZ, fold
from bar_adapters import base_event

MONTHS = {name: index for index, name in enumerate([
    "janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"], 1)}


def text(soup, selector):
    node = soup.select_one(selector)
    return node.get_text(" ", strip=True) if node else ""


def dotted_day(value):
    match = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", value)
    try:
        return date(int(match[3]), int(match[2]), int(match[1])) if match else None
    except ValueError:
        return None


def clock(value):
    match = re.fullmatch(r"\s*(\d{1,2})\s*[hH:]\s*(\d{2})?\s*", value)
    try:
        return time(int(match[1]), int(match[2] or 0)) if match else None
    except ValueError:
        return None


def set_start(event, day, hour):
    if day and hour:
        start = datetime.combine(day, hour, TZ)
        # ZoneInfo attaches an offset even to a nonexistent spring time.
        if start.astimezone(timezone.utc).astimezone(TZ).replace(tzinfo=None) != start.replace(tzinfo=None):
            return
        if start.replace(fold=0).utcoffset() != start.replace(fold=1).utcoffset():
            return  # autumn clock change: offset not supplied by this source
        event.update(date=day.isoformat(), time=hour.strftime("%H:%M"), start_at=start.isoformat())


def metadata(soup, name):
    node = soup.select_one(f'meta[property="{name}"]')
    return node.get("content", "") if node else ""


from samstag.collection.adapters.docks import parse_docks
from samstag.collection.adapters.dclub import collect_dclub, parse_dclub
from samstag.collection.adapters.docks_romandie import collect_docks_romandie
from samstag.collection.adapters.jumeaux import parse_jumeaux
from samstag.collection.adapters.chorus import parse_chorus
from samstag.collection.adapters.bellevaux import parse_bellevaux


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


def collect_venue(url, soup, fetch):
    host = (urlparse(url).hostname or "").removeprefix("www.")
    if host == "chorus.ch":
        return parse_chorus(soup, url), "chorus-programme-v1 (mois et année publiés)"
    if host == "cinemabellevaux.ch":
        return parse_bellevaux(soup, url), "bellevaux-sessions-v1 (période explicite, séances distinctes)"
    if host == "dclub.ch":
        return collect_dclub(soup, url, fetch)
    if host == "jumeaux.club":
        return parse_jumeaux(soup, url), "jumeaux-html-v1"
    if host == "lausanne-tourisme.ch" and re.match(r"^/fr/evenement/[^/]+/?$", urlparse(url).path):
        event = parse_tourisme(soup, url)
        return ([event] if event else []), "tourisme-detail-v1"
    if host in {"docks.ch", "leromandie.ch"}:
        return collect_docks_romandie(soup, url, fetch)
    return None
