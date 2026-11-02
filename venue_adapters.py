"""Site-specific readers, based on inspected public programme pages."""
import json
import logging
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import TZ, fold
from bar_adapters import base_event
from config import config

log = logging.getLogger(__name__)
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
    from collection_result import CollectionResult
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
    from scraper import _extract_jsonld_events, FetchError
    from collection_result import CollectionResult
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
        pattern = r"^/evenement/concerts/\d{8}/[^/]+/?$" if host == "docks.ch" else r"^/event/[^/]+/?$"
        links = []
        for link in soup.select("a[href]"):
            target = urljoin(url, link["href"]).split("#")[0]
            if urlparse(target).hostname == urlparse(url).hostname and re.match(pattern, urlparse(target).path) and target not in links:
                if host == "docks.ch":
                    match = re.search(r"/concerts/(\d{8})/", target)
                    try:
                        day = datetime.strptime(match[1], "%Y%m%d").date()
                        today = datetime.now(TZ).date()
                        if day < today or day > today+timedelta(days=config.COLLECTION_HORIZON_DAYS):
                            continue
                    except (ValueError, TypeError):
                        pass
                links.append(target)
        # The list is already in programme order. Limit each run, but retain
        # the discovered count in diagnostics so limits cannot look exhaustive.
        events, failures = [], 0
        for target in links[:config.MAX_DETAIL_PAGES]:
            try:
                detail = BeautifulSoup(fetch(target), "lxml")
                if host == "docks.ch":
                    event = parse_docks(detail, target)
                    events.append(event)
                else:
                    for event in _extract_jsonld_events(detail, target):
                        event.update(adapter="romandie-jsonld-v1", source_event_key=target)
                        # The official Event.startDate is explicitly labelled
                        # portes in the visible programme: keep that distinction.
                        event["time_role"] = "doors"
                        artist_headings = [fold(h.get_text(" ", strip=True)) for h in detail.select("h2")]
                        if artist_headings and set(artist_headings) == {"dj"}:
                            event.update(event_kind="ClubNight", category="Clubbing")
                        events.append(event)
            except (FetchError, ValueError, TypeError) as exc:
                failures += 1
                log.warning("Programme detail failed %s: %s", target, exc)
        checked = min(len(links), config.MAX_DETAIL_PAGES)
        read = checked - failures
        parse_status = "error" if checked and failures == checked else "partial" if failures else "ok"
        completeness = "limited" if len(links) > checked else "partial" if failures else "complete"
        return CollectionResult(
            events,
            f"{host}: {len(links)} liens, {checked} contrôlés, {failures} erreurs",
            complete_snapshot=not failures and len(links) <= checked,
            partial=bool(failures or len(links) > checked),
            pages_expected=len(links),
            pages_read=read,
            parse_status=parse_status,
            completeness_status=completeness,
        )
    return None
