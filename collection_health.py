"""Actionable collection health, separate from web-process availability."""
import time
from collections import Counter

import db
from source_registry import SOURCES, active_sources


def health(now=None):
    now = time.time() if now is None else now
    run = db.latest_collection_run()
    diagnostics = {row["source_url"]: row for row in db.source_run_diagnostics(
        run["run_id"] if run else None
    )}
    legacy = {row["url"]: row for row in db.source_status()}
    states = Counter()
    incidents, limitations, sources = [], [], []

    for source in active_sources():
        url = source["canal"]
        row = diagnostics.get(url)
        old = legacy.get(url)
        checked_at = row["checked_at"] if row else old["timestamp"] if old else None
        incident = None
        known = []
        if checked_at is None:
            incident = "never_collected"
        elif now - checked_at > 86400:
            incident = "stale"
        elif row and row["access_status"] == "error":
            incident = "access_error"
        elif row and row["parse_status"] in {"error", "not_run"}:
            incident = "parse_error"
        elif not row and old and old["status"] == "error":
            incident = "collection_error"

        if row:
            if row["parse_status"] == "unsupported":
                known.append("needs_adapter")
            if row["completeness_status"] in {"partial", "limited"}:
                known.append(f"coverage_{row['completeness_status']}")
            if row["editorial_status"] == "review_required":
                known.append("editorial_review_required")
        elif old and old["status"] in {"partial", "needs_adapter"}:
            known.append(old["status"])

        state = incident or ("limited" if known else "ok")
        states[state] += 1
        entry = {
            "source_id": source["id"], "name": source["nom"], "url": url,
            "status": state, "automatic": source["auto_publish"],
            "checked_at": checked_at, "limitations": known,
        }
        if row:
            entry["dimensions"] = {
                key: row[key] for key in (
                    "access_status", "parse_status", "completeness_status", "editorial_status"
                )
            }
            entry["counts"] = {
                key: row[key] for key in (
                    "pages_expected", "pages_read", "observations", "candidates",
                    "rejected", "published", "withdrawn"
                )
            }
        sources.append(entry)
        if incident:
            incidents.append(entry)
        elif known:
            limitations.append(entry)

    missing_from_run = bool(run and run["sources_checked"] < run["sources_expected"])
    return {
        "status": "degraded" if incidents or missing_from_run else "ok",
        "sources": len(sources), "states": dict(states),
        "registry": {
            "configured": len(SOURCES), "active": len(active_sources()),
            "disabled": [source["id"] for source in SOURCES if not source["enabled"]],
        },
        "run": run, "incidents": incidents, "known_limitations": limitations,
        "coverage": sources,
    }
