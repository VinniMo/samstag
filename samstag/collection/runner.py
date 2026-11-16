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

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import db
from config import config

from .http import FetchError, _fetch
from .parsers.common import CATEGORY_RULES, LOCAL_TZ, _gen_id, _parse_iso_date, categorize
from .parsers.html import _detail_links, _detail_pattern, _extract_html_events, _parse_card
from .parsers.ical import _ics_date, _ics_value, _unfold_ics, parse_ics
from .parsers.jsonld import (
    EVENT_TYPES,
    _extract_image,
    _extract_jsonld_events,
    _extract_location,
    _extract_price,
    _is_event,
    _jsonld_items,
    _normalize_jsonld,
)
from .result import CollectionResult

logger = logging.getLogger("scraper")


class ParseError(Exception):
    pass


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
    except (ValueError, TypeError, KeyError) as exc:
        raise ParseError(str(exc)) from exc
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


def scrape_sources(sources: Iterable[str] | None = None, run_id: str | None = None) -> list[dict]:
    """Scrape every source URL and return a deduplicated list of events."""
    from collection_quality import assess
    from source_registry import source_for
    sources = tuple(dict.fromkeys(config.SCRAPE_SOURCES if sources is None else sources))
    aggregated: dict[str, dict] = {}
    own_run = run_id is None
    run_id = run_id or db.start_collection_run(len(sources))
    run_degraded = False

    # Fetch sources concurrently; persist on this thread for deterministic,
    # short SQLite transactions. One failing parser cannot stop the pass.
    with ThreadPoolExecutor(max_workers=config.COLLECTION_WORKERS) as pool:
        jobs = {pool.submit(scrape_one, url): url for url in sources}
        for job in as_completed(jobs):
            url = jobs[job]
            source = source_for(url)
            editorial = ("automatic" if source and source.get("auto_publish") else
                         "review_required" if source else "unregistered")
            try:
                result = CollectionResult.normalize(job.result())
                found, method = result
            except Exception as exc:
                logger.warning("Collection failed for %s: %s", url, exc)
                db.log_scrape("scraper", url, "error", 0, str(exc)[:300])
                access = "error" if isinstance(exc, FetchError) else "ok"
                parse = "not_run" if isinstance(exc, FetchError) else "error"
                db.log_source_run(
                    run_id, url, source_id=source.get("id") if source else None,
                    access_status=access, parse_status=parse,
                    completeness_status="unknown", editorial_status=editorial,
                    message=str(exc)[:300],
                )
                run_degraded = True
                continue
            seen_ids = set()
            malformed = candidates = rejected = 0
            for evt in found:
                try:
                    item = assess(evt, url)
                except (ValueError, TypeError, AttributeError) as exc:
                    logger.warning("Malformed record from %s: %s", url, exc)
                    malformed += 1
                    continue
                if item["status"] == "candidate":
                    candidates += 1
                else:
                    rejected += 1
                db.stage_collection(item)
                seen_ids.add(item["event"]["id"])
                aggregated[item["event"]["id"]] = item["event"]
            partial = bool(result.partial or malformed)
            withdrawn = 0
            if result.complete_snapshot and not partial:
                withdrawn = db.reconcile_source_snapshot(url, seen_ids)
            parse_status = result.parse_status
            if malformed and parse_status == "ok":
                parse_status = "partial"
            unsupported = method.startswith(("html", "embedded-calendar"))
            if unsupported:
                parse_status = "unsupported"
            status = ("partial" if partial else "ok" if found else
                      "needs_adapter" if unsupported else "empty")
            db.log_scrape("scraper", url, status, len(found), method)
            db.log_source_run(
                run_id, url, source_id=source.get("id") if source else None,
                access_status=result.access_status, parse_status=parse_status,
                completeness_status=result.completeness_status,
                editorial_status=editorial, pages_expected=result.pages_expected,
                pages_read=result.pages_read, observations=len(found),
                candidates=candidates, rejected=rejected,
                published=db.public_count_for_source(url), withdrawn=withdrawn,
                message=method,
            )
            run_degraded = run_degraded or status in {"error", "partial"}
            logger.info("Scraped %d events from %s (%s)", len(found), url, method)

    diagnostics = db.source_run_diagnostics(run_id)
    if len(diagnostics) < len(sources):
        run_degraded = True
    db.finish_collection_run(run_id, "degraded" if run_degraded else "ok")
    if own_run:
        db.prune_collection_diagnostics(config.COLLECTION_LOG_RETENTION_DAYS)
    return list(aggregated.values())


def refresh_database() -> int:
    """Refresh qualified sources, with a lease shared by Flask/CLI workers."""
    with db.collection_lease() as acquired:
        return len(scrape_sources()) if acquired else 0
