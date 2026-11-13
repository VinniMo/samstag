"""Site-specific readers, based on inspected public programme pages."""
import re
from datetime import date, datetime, time, timezone
from urllib.parse import urlparse

from agenda import TZ

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
from samstag.collection.adapters.tourisme import parse_tourisme


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
