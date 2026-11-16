"""Schema.org event extraction from JSON-LD."""
import json
import logging
from typing import Iterable

from bs4 import BeautifulSoup

from .common import _gen_id, _parse_iso_date, categorize

logger = logging.getLogger("scraper")


EVENT_TYPES = {
    "Event", "MusicEvent", "TheaterEvent", "DanceEvent",
    "VisualArtsEvent", "Festival", "ExhibitionEvent",
    "ScreeningEvent", "ComedyEvent",
}


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
