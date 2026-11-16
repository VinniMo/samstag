"""Generic HTML fallback and event-detail link discovery."""
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from config import config
from .common import LOCAL_TZ, _gen_id, categorize


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
