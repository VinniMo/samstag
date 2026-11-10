"""Bounded detail traversal shared by Docks and Le Romandie programmes."""

import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import TZ, fold
from collection_result import CollectionResult
from config import config

from .docks import parse_docks

log = logging.getLogger(__name__)


def collect_docks_romandie(soup, url, fetch):
    from scraper import _extract_jsonld_events, FetchError

    host = (urlparse(url).hostname or "").removeprefix("www.")
    if host not in {"docks.ch", "leromandie.ch"}:
        return None
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
                    if day < today or day > today + timedelta(days=config.COLLECTION_HORIZON_DAYS):
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
                events.append(parse_docks(detail, target))
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
