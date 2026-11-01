"""Scraper for Lausanne samstagl sources.

Strategy, for each configured source URL:
    1. iCalendar feed (BEGIN:VCALENDAR): read its VEVENT entries.
    2. JSON-LD structured data (schema.org/Event variants) on the page.
    3. Listing pages of known aggregators (config.DETAIL_LINK_PATTERNS):
       follow the links to each event page and read its JSON-LD.
    4. Fall back to HTML heuristics.

Every source run is logged with the method used and the number of events
found, so /api/sources can show which sources actually work.

The scraper is intentionally defensive: any individual page failure is
logged and skipped, never raised.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from zoneinfo import ZoneInfo
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from config import config
import db
from collection_result import CollectionResult

logger = logging.getLogger(__name__)

LOCAL_TZ = ZoneInfo("Europe/Zurich")

EVENT_TYPES = {
    "Event", "MusicEvent", "TheaterEvent", "DanceEvent",
    "VisualArtsEvent", "Festival", "ExhibitionEvent",
    "ScreeningEvent", "ComedyEvent",
}

CATEGORY_RULES: dict[str, tuple[str, ...]] = {
    # Order matters — first match wins. Clubbing before Musique to catch DJ/techno.
    "Clubbing":  ("techno", "house", "club night", "after", "rave", "warehouse",
                  "underground", "boiler room", "dj set", "afterhour", "all night",
                  "d! club", "mad club", "folklore", "datcha"),
    "Musique":   ("concert", "jazz", "rock", "classique", "opéra", "orchestre",
                  "récital", "électronique", "electro", "dj", "chanson", "vivaldi",
                  "beethoven", "brahms", "verdi", "live band", "punk", "metal",
                  "indie", "pop", "folk", "hip-hop", "rap"),
    "Théâtre":   ("théâtre", "pièce", "comédie", "tragédie", "hamlet",
                  "molière", "mise en scène", "spectacle", "monologue"),
    "Exposition": ("exposition", "expo", "vernissage", "galerie",
                   "rétrospective", "musée", "installation"),
    "Cinéma":    ("cinéma", "film", "projection", "documentaire",
                  "court-métrage", "ciné", "avant-première"),
    "Danse":     ("danse", "ballet", "chorégraphie", "flamenco",
                  "contemporain", "performance"),
    "Festival":  ("festival", "fête", "nuit des musées", "open air"),
    "Famille":   ("famille", "enfants", "jeune public", "marionnettes"),
    "Conférence": ("conférence", "débat", "symposium", "lecture", "talk"),
    "Sport":     ("sport", "marathon", "course", "match", "tournoi"),
    "Humour":    ("humour", "comedy", "stand-up", "one-man-show"),
    "Atelier":   ("atelier", "workshop", "initiation"),
    "Marché":    ("marché", "foire", "artisanat"),
}


def _gen_id(title: str, date: str) -> str:
    return hashlib.md5(f"{title}|{date}".encode("utf-8")).hexdigest()[:10]


def categorize(title: str, description: str = "") -> str:
    text = f"{title} {description}".lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(kw in text for kw in keywords):
            return category
    return "Culture"


def _parse_iso_date(value: str) -> tuple[str, str]:
    if not value:
        return "", ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value[:10], ""
    if dt.tzinfo is not None:
        dt = dt.astimezone(LOCAL_TZ)
    # A bare date ("2026-10-16") carries no time: do not show "00:00".
    has_time = "T" in value or " " in value.strip()
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M") if has_time else ""


def _extract_image(image_field) -> str:
    if isinstance(image_field, list) and image_field:
        first = image_field[0]
        return first if isinstance(first, str) else first.get("url", "")
    if isinstance(image_field, dict):
        return image_field.get("url", "")
    if isinstance(image_field, str):
        return image_field
    return ""


def _extract_location(location_field) -> tuple[str, str]:
    if isinstance(location_field, dict):
        name = location_field.get("name", "")
        address = location_field.get("address", "")
        if isinstance(address, dict):
            parts = [
                address.get("streetAddress", ""),
                address.get("postalCode", ""),
                address.get("addressLocality", ""),
            ]
            address = ", ".join(p for p in parts if p)
        return name, address
    if isinstance(location_field, str):
        return location_field, ""
    return "", ""


def _extract_price(offers) -> str:
    """Price text from schema.org offers, or "" when the source gives none."""
    if isinstance(offers, list):
        texts = [t for t in (_extract_price(o) for o in offers) if t]
        return " / ".join(dict.fromkeys(texts))
    if not isinstance(offers, dict):
        return ""
    low, high = offers.get("lowPrice"), offers.get("highPrice")
    price = offers.get("price", low)
    currency = offers.get("priceCurrency") or "CHF"
    try:
        if price is not None and float(str(price).replace(",", ".")) == 0:
            return "Gratuit"
    except ValueError:
        return str(price).strip()
    if low is not None and high is not None and str(low) != str(high):
        return f"{currency} {low}–{high}"
    return f"{currency} {price}" if price not in (None, "") else ""


def _normalize_jsonld(item: dict, page_url: str = "") -> dict | None:
    title = (item.get("name") or "").strip()
    if not title:
        return None

    date, time_str = _parse_iso_date(item.get("startDate", ""))
    end_date, _ = _parse_iso_date(item.get("endDate", ""))
    location_field = item.get("location")
    if isinstance(location_field, list):
        location_field = location_field[0] if location_field else None
    location, address = _extract_location(location_field)
    description = BeautifulSoup(item.get("description") or "", "lxml").get_text(" ", strip=True)[:400]
    price = _extract_price(item.get("offers"))
    if not price and item.get("isAccessibleForFree") in (True, "true", "True"):
        price = "Gratuit"

    return {
        "id": _gen_id(title, date),
        "start_at": item.get("startDate", ""),
        "end_at": item.get("endDate", ""),
        "event_kind": next((t for t in (item.get("@type") if isinstance(item.get("@type"), list) else [item.get("@type")]) if t in EVENT_TYPES and t != "Event"), ""),
        "event_status": (item.get("eventStatus") or "").rsplit("/", 1)[-1],
        "municipality": ((location_field.get("address") or {}).get("addressLocality", "")
                         if isinstance(location_field, dict) and isinstance(location_field.get("address"), dict) else ""),
        "evidence_url": page_url,
        "title": title,
        "date": date,
        "time": time_str,
        "end_date": end_date,
        "location": location,
        "address": address,
        "category": categorize(title, description),
        "subcategory": "",
        "description": description,
        "image": _extract_image(item.get("image")),
        "price": price,
        "url": item.get("url") or page_url,
        "tags": [],
        "featured": False,
    }


def _jsonld_items(data) -> Iterable[dict]:
    """Walk JSON-LD: plain objects, lists and @graph containers."""
    if isinstance(data, list):
        for entry in data:
            yield from _jsonld_items(entry)
    elif isinstance(data, dict):
        yield data
        for value in data.values():
            if isinstance(value, (dict, list)):
                yield from _jsonld_items(value)


def _is_event(item: dict) -> bool:
    kind = item.get("@type")
    kinds = kind if isinstance(kind, list) else [kind]
    return any(k in EVENT_TYPES for k in kinds)


def _extract_jsonld_events(soup: BeautifulSoup, page_url: str = "") -> list[dict]:
    events: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in _jsonld_items(data):
            try:
                if not _is_event(item):
                    continue
                normalized = _normalize_jsonld(item, page_url)
            except (ValueError, TypeError, AttributeError):
                logger.warning("Malformed structured event skipped on %s", page_url)
                continue
            if normalized:
                events.append(normalized)
    return events


def _unfold_ics(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _ics_value(value: str) -> str:
    return (value.replace("\\n", " ").replace("\\N", " ").replace("\\,", ",")
            .replace("\\;", ";").replace("\\\\", "\\").strip())


def _ics_date(key: str, value: str) -> tuple[str, str]:
    """DTSTART / DTEND: date-only, local, or UTC (Z) values."""
    value = value.strip()
    if "VALUE=DATE" in key and len(value) == 8:
        return f"{value[:4]}-{value[4:6]}-{value[6:]}", ""
    m = re.match(r"(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})\d{0,2}(Z?))?$", value)
    if not m:
        return "", ""
    y, mo, d, hh, mm, utc = m.groups()
    if hh is None:
        return f"{y}-{mo}-{d}", ""
    iso = f"{y}-{mo}-{d}T{hh}:{mm}:00" + ("+00:00" if utc else "")
    return _parse_iso_date(iso)


def parse_ics(text: str, page_url: str = "") -> list[dict]:
    """Read VEVENT entries from an iCalendar feed."""
    events: list[dict] = []
    current: dict[str, str] | None = None
    for line in _unfold_ics(text):
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT" and current is not None:
            title = _ics_value(current.get("SUMMARY", ""))
            date, time_str = current.get("_start", ("", ""))
            end_date, _ = current.get("_end", ("", ""))
            if title:
                description = _ics_value(current.get("DESCRIPTION", ""))[:400]
                location = _ics_value(current.get("LOCATION", ""))
                venue, _, address = location.partition(",")
                events.append({
                    "id": _gen_id(title, date), "title": title, "date": date,
                    "time": time_str, "end_date": end_date if end_date != date else "",
                    "location": venue.strip(), "address": address.strip(),
                    "category": categorize(title, description), "subcategory": "",
                    "description": description, "image": "", "price": "",
                    "url": current.get("URL", "").strip() or page_url,
                    "tags": [], "featured": False,
                })
            current = None
        elif current is not None and ":" in line:
            key, _, value = line.partition(":")
            name = key.split(";")[0].upper()
            if name == "DTSTART":
                current["_start"] = _ics_date(key, value)
            elif name == "DTEND":
                current["_end"] = _ics_date(key, value)
            else:
                current[name] = value
    return events


def _detail_links(soup: BeautifulSoup, page_url: str, pattern: str) -> list[str]:
    """Event-page links on an aggregator listing page, in page order."""
    rule = re.compile(pattern)
    host = urlparse(page_url).netloc
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        url = urljoin(page_url, a["href"]).split("#")[0]
        if urlparse(url).netloc == host and rule.search(urlparse(url).path) and url not in links:
            links.append(url)
    # Tourism listings are not necessarily chronological. Prefer cards with
    # explicit dates in the current horizon, keeping unknown dates behind them.
    if "lausanne-tourisme.ch" in host:
        from venue_adapters import dotted_day
        dates = {}
        for anchor in soup.select("a[href]"):
            target = urljoin(page_url, anchor["href"]).split("#")[0]
            if target in links:
                try:
                    dates[target] = dotted_day(anchor.get_text(" ", strip=True))
                except ValueError:
                    pass
        today = datetime.now(LOCAL_TZ).date()
        def score(target):
            day = dates.get(target)
            if day and today <= day <= today+timedelta(days=28):
                return 0, day.isoformat()
            return (1 if day is None else 2), day.isoformat() if day else ""
        links.sort(key=score)
    return links


def _detail_pattern(url: str) -> str | None:
    host = urlparse(url).netloc.lower()
    for domain, pattern in config.DETAIL_LINK_PATTERNS:
        if host == domain or host.endswith("." + domain):
            return pattern
    return None


def _extract_html_events(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Heuristic fallback: scan for elements that look like event cards."""
    selector = re.compile(r"event|agenda|card|show|spectacle|concert", re.IGNORECASE)
    candidates = soup.find_all(["article", "li", "div"], class_=selector, limit=80)

    events: list[dict] = []
    for card in candidates:
        evt = _parse_card(card, base_url)
        if evt:
            events.append(evt)
    return events


def _parse_card(card: Tag, base_url: str) -> dict | None:
    title_tag = card.find(["h1", "h2", "h3", "h4"])
    if not title_tag:
        return None
    title = title_tag.get_text(strip=True)
    if not title or len(title) < 4:
        return None

    time_tag = card.find("time")
    date = ""
    if time_tag:
        date = (time_tag.get("datetime") or time_tag.get_text(strip=True))[:10]
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None  # headings/navigation without an actual date are not events

    desc_tag = card.find("p")
    description = desc_tag.get_text(strip=True)[:400] if desc_tag else ""

    img_tag = card.find("img")
    image = ""
    if img_tag:
        image = img_tag.get("src", "") or img_tag.get("data-src", "")
        if image:
            image = urljoin(base_url, image)

    link_tag = card.find("a", href=True)
    url = urljoin(base_url, link_tag["href"]) if link_tag else ""

    return {
        "id": _gen_id(title, date),
        "title": title,
        "date": date,
        "time": "",
        "end_date": "",
        "location": "",
        "address": "",
        "category": categorize(title, description),
        "subcategory": "",
        "description": description,
        "image": image,
        "price": "",
        "url": url,
        "tags": [],
        "featured": False,
    }


class FetchError(Exception):
    pass


def _fetch(url: str, extra_headers: dict | None = None) -> str:
    headers = {
        "User-Agent": config.SCRAPE_USER_AGENT,
        "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.5",
    }
    headers.update(extra_headers or {})
    try:
        resp = requests.get(url, headers=headers, timeout=config.SCRAPE_TIMEOUT_SECONDS)
        resp.raise_for_status()
        # Several venue servers omit charset and requests otherwise uses Latin-1.
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except requests.RequestException as exc:
        raise FetchError(str(exc)) from exc


def scrape_one(url: str) -> tuple[list[dict], str] | CollectionResult:
    """Collect one source. Returns (events, method used). Raises FetchError."""
    text = _fetch(url)
    if text.lstrip().startswith("BEGIN:VCALENDAR"):
        return parse_ics(text, url), "ical"

    soup = BeautifulSoup(text, "lxml")
    from venue_adapters import collect_venue
    from bar_adapters import collect_bar
    from hango_adapter import collect_hango
    from expanded_adapters import collect_expanded
    from programme_adapters import collect_programme
    try:
        specialized = collect_programme(url, soup, _fetch)
        if specialized is None:
            specialized = collect_expanded(url, soup, _fetch)
        if specialized is None:
            specialized = collect_venue(url, soup, _fetch)
        if specialized is None:
            specialized = collect_hango(url, soup, _fetch)
        if specialized is None:
            specialized = collect_bar(url, soup, _fetch)
    except (ValueError, TypeError) as exc:
        raise FetchError(str(exc)) from exc
    if specialized is not None:
        return specialized
    found = _extract_jsonld_events(soup, url)
    if found:
        return found, "json-ld"

    pattern = _detail_pattern(url)
    if pattern:
        targets = _detail_links(soup, url, pattern)
        links = targets[: config.MAX_DETAIL_PAGES]
        failures = 0
        for link in links:
            try:
                page = BeautifulSoup(_fetch(link), "lxml")
            except FetchError as exc:
                logger.warning("Detail page failed %s: %s", link, exc)
                failures += 1
                continue
            structured = _extract_jsonld_events(page, link)
            if structured:
                found.extend(structured)
            elif (urlparse(link).hostname or "").endswith("lausanne-tourisme.ch"):
                from venue_adapters import parse_tourisme
                try:
                    event = parse_tourisme(page, link)
                    if event:
                        found.append(event)
                except (ValueError, TypeError, KeyError) as exc:
                    logger.warning("Tourisme detail malformed %s: %s", link, exc)
                    failures += 1
        return CollectionResult(found, f"pages-detail ({len(links)}/{len(targets)} liens, {failures} erreurs)",
                                partial=bool(failures or len(targets) > len(links)))

    if soup.select("iframe[src*='backoffice.hango.ch']"):
        return [], "embedded-calendar: adaptateur Hango à étudier"
    return _extract_html_events(soup, base_url=url), "html (validation requise)"


def scrape_sources(sources: Iterable[str] | None = None) -> list[dict]:
    """Scrape every source URL and return a deduplicated list of events."""
    from collection_quality import assess
    sources = config.SCRAPE_SOURCES if sources is None else sources
    aggregated: dict[str, dict] = {}

    # Fetch sources concurrently; persist on this thread for deterministic,
    # short SQLite transactions. One failing parser cannot stop the pass.
    with ThreadPoolExecutor(max_workers=config.COLLECTION_WORKERS) as pool:
        jobs = {pool.submit(scrape_one, url): url for url in dict.fromkeys(sources)}
        for job in as_completed(jobs):
            url = jobs[job]
            try:
                result = job.result()
                found, method = result
            except Exception as exc:
                logger.warning("Collection failed for %s: %s", url, exc)
                db.log_scrape("scraper", url, "error", 0, str(exc)[:300])
                continue
            seen_ids = set()
            malformed = 0
            for evt in found:
                try:
                    item = assess(evt, url)
                except (ValueError, TypeError, AttributeError) as exc:
                    logger.warning("Malformed record from %s: %s", url, exc)
                    malformed += 1
                    continue
                db.stage_collection(item)
                seen_ids.add(item["event"]["id"])
                aggregated[item["event"]["id"]] = item["event"]
            partial = bool(getattr(result, "partial", False) or malformed)
            if getattr(result, "complete_snapshot", False) and not partial:
                db.reconcile_source_snapshot(url, seen_ids)
            status = ("partial" if partial else "ok" if found else
                      "needs_adapter" if method.startswith(("html", "embedded-calendar")) else "empty")
            db.log_scrape("scraper", url, status, len(found), method)
            logger.info("Scraped %d events from %s (%s)", len(found), url, method)

    return list(aggregated.values())


def refresh_database() -> int:
    """Refresh qualified sources, with a lease shared by Flask/CLI workers."""
    with db.collection_lease() as acquired:
        return len(scrape_sources()) if acquired else 0
