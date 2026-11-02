"""Local operational report; evaluates alerts without sending or collecting."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import db
from collection_health import health
from deploy.infomaniak.backup import DEFAULT_BACKUP_DIR

SOURCE_WARNING_SECONDS = 18 * 3600
SOURCE_CRITICAL_SECONDS = 24 * 3600
BACKUP_WARNING_SECONDS = 20 * 3600
BACKUP_CRITICAL_SECONDS = 24 * 3600
ERROR_STATES = {"access_error", "parse_error", "collection_error", "never_collected", "stale"}


def evaluate_sources(coverage: list[dict], statuses: list[dict], now: float) -> list[dict]:
    latest = {row["url"]: row for row in statuses}
    alerts = []
    for source in coverage:
        if not source.get("automatic"):
            continue
        row = latest.get(source["url"], {})
        last_success = row.get("last_success")
        if last_success is None:
            level, reason, age_hours = "critical", "never_successful", None
        else:
            age_seconds = max(0, now - last_success)
            age_hours = round(age_seconds / 3600, 1)
            if age_seconds >= SOURCE_CRITICAL_SECONDS:
                level, reason = "critical", "last_success_24h"
            elif age_seconds >= SOURCE_WARNING_SECONDS:
                level, reason = "warning", "last_success_18h"
            elif source.get("status") in ERROR_STATES:
                level, reason = "warning", "current_collection_error"
            else:
                continue
        alerts.append({
            "level": level,
            "kind": "source",
            "source_id": source["source_id"],
            "name": source["name"],
            "reason": reason,
            "hours_since_success": age_hours,
        })
    return alerts


def evaluate_backup(folder: Path, now: float) -> list[dict]:
    files = list(Path(folder).glob("samstag-*.sqlite3"))
    if not files:
        return [{"level": "critical", "kind": "backup", "reason": "missing_backup"}]
    newest = max(files, key=lambda path: path.stat().st_mtime)
    age_seconds = max(0, now - newest.stat().st_mtime)
    if age_seconds >= BACKUP_CRITICAL_SECONDS:
        level, reason = "critical", "backup_24h"
    elif age_seconds >= BACKUP_WARNING_SECONDS:
        level, reason = "warning", "backup_20h"
    else:
        return []
    return [{
        "level": level,
        "kind": "backup",
        "reason": reason,
        "hours_since_backup": round(age_seconds / 3600, 1),
        "file": newest.name,
    }]


def build_report(backup_dir: Path = DEFAULT_BACKUP_DIR, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    collection = health(now=now)
    alerts = evaluate_sources(collection["coverage"], db.source_status(), now)
    alerts.extend(evaluate_backup(backup_dir, now))
    alerts.sort(key=lambda item: (item["level"] != "critical", item["kind"], item.get("source_id", "")))
    return {
        "status": "critical" if any(a["level"] == "critical" for a in alerts)
                  else "warning" if alerts else "ok",
        "generated_at": now,
        "alerts": alerts,
        "collection_summary": collection["states"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    args = parser.parse_args()
    report = build_report(args.backup_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit({"ok": 0, "warning": 1, "critical": 2}[report["status"]])


if __name__ == "__main__":
    main()
