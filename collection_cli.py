"""Local collection / review, using SAMSTAG_DB (no Render integration)."""
import argparse
import json

import db
import scraper
from config import config
from source_registry import SOURCES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["collect", "list", "approve", "sources", "report",
                                             "match-duplicates", "unmatch-duplicate"])
    parser.add_argument("event_id", nargs="?")
    parser.add_argument("--source", action="append", default=[], help="Identifiant configuré, répétable (ex. SRC_L001)")
    args = parser.parse_args()
    db.init_db()
    if args.command == "collect":
        selected = [s["canal"] for s in SOURCES if s["id"] in args.source]
        if args.source and len(selected) != len(set(args.source)):
            parser.error("Identifiant de source inconnu")
        if args.source:
            with db.collection_lease() as acquired:
                count = len(scraper.scrape_sources(selected)) if acquired else 0
        else:
            count = scraper.refresh_database()
        print(json.dumps({"collected": count, "public": len(db.list_public_events())}))
    elif args.command == "list":
        print(json.dumps(db.collection_items(), ensure_ascii=False, indent=2))
    elif args.command == "sources":
        print(json.dumps(SOURCES, ensure_ascii=False, indent=2))
    elif args.command == "report":
        from collections import Counter
        from datetime import datetime
        from agenda import TZ
        from collection_report import coverage, duplicate_candidates
        enabled_urls = {s["canal"] for s in SOURCES if s["enabled"]}
        statuses = db.source_status()
        print(json.dumps({"generated_at":datetime.now(TZ).isoformat(),
                          "configured_sources":len(SOURCES), "enabled_sources":sum(s["enabled"] for s in SOURCES),
                          "automatic_channels":sum(s["enabled"] and s["auto_publish"] for s in SOURCES),
                          "sources": [s for s in statuses if s["url"] in enabled_urls],
                          "latest_run": db.latest_collection_run(),
                          "source_diagnostics": db.source_run_diagnostics(),
                          "technical_log_retention_days": config.COLLECTION_LOG_RETENTION_DAYS,
                          "historical_checks": [s for s in statuses if s["url"] not in enabled_urls],
                          "decisions_at_collection": dict(Counter(i["status"] for i in db.collection_items())),
                          "public": len(db.list_public_events()), "reasons": dict(Counter(i["reason"] for i in db.collection_items())),
                          "coverage": coverage(),
                          "possible_duplicates": duplicate_candidates(),
                          "active_duplicate_matches": db.duplicate_matches()}, ensure_ascii=False, indent=2))
    elif args.command == "match-duplicates":
        print(json.dumps(db.apply_safe_duplicate_matches(), ensure_ascii=False, indent=2))
    elif args.command == "unmatch-duplicate":
        if not args.event_id:
            parser.error("unmatch-duplicate requiert l'identifiant de la fiche rapprochée")
        print(json.dumps({"restored": db.undo_duplicate_match(args.event_id),
                          "event_id": args.event_id}, ensure_ascii=False))
    elif not args.event_id:
        parser.error("approve requiert l'identifiant de l'événement")
    else:
        try:
            db.approve_collection(args.event_id)
        except ValueError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    main()
