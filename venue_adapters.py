"""Site-specific readers, based on inspected public programme pages."""
import json
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

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
                    hour = clock(opening[1]); event["doors_time"] = hour.strftime("%H:%M") if hour else ""
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
                    set_start(event, date(year,month,int(match[1])), clock(text(card,".event_time")))
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


def parse_bellevaux(soup, url):
    events = []
    for card in soup.select(".block-default"):
        link = card.select_one(".block-default-header a[href]")
        if not link:
            continue
        detail = urljoin(url, link["href"])
        if urlparse(detail).hostname != urlparse(url).hostname:
            continue
        period = re.match(r"^/(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{4})/", urlparse(detail).path)
        if not period:
            continue
        try:
            first = date(int(period[5]), int(period[2]), int(period[1]))
            last = date(int(period[5]), int(period[4]), int(period[3]))
            if not timedelta(0) <= last-first <= timedelta(days=7):
                continue  # ambiguous year boundary, not normalized by guessing
        except ValueError:
            continue
        schedule = fold(text(card, ".block-default-overtitle"))
        sessions = [(int(m[1]),int(m[2]),m[3]) for m in re.finditer(r"(\d{1,2})\.(\d{1,2})\s+a\s+(\d{1,2}:\d{2})",schedule)]
        for match in re.finditer(r"(\d{1,2})\s+(\w+)\s+a\s+(\d{1,2}:\d{2})",schedule):
            if match[2] in MONTHS:
                sessions.append((int(match[1]),MONTHS[match[2]],match[3]))
        for day_number, month, hour in sessions:
            try:
                day = date(first.year, month, day_number)
            except ValueError:
                continue
            if not first <= day <= last:
                continue
            event = base_event(text(card, "h3"), detail, url)
            if not event["title"]:
                continue
            event.update(location="Cinéma Bellevaux", municipality="Lausanne", event_kind="ScreeningEvent",
                         category="Cinéma", adapter="bellevaux-v1", series_id=detail,
                         date_basis="explicit programme-week URL + published session day/month")
            set_start(event, day, clock(hour))
            event["description"] = text(card, ".visible-xs")[:400]
            image = card.select_one(".block-default-img img[src]")
            event["image"] = urljoin(url, image["src"]) if image else ""
            events.append(event)
    return events


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
