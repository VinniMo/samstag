"""Run scheduled collections independently of web traffic.

Use the same LAUSANNE_DB as Flask. This process does not deploy anything.
SIGTERM/SIGINT allow the current bounded collection to finish, then stop.
"""
import argparse
import json
import logging
import signal
import threading
import time
from datetime import datetime

import db
import scraper
from agenda import TZ
from config import config

log = logging.getLogger(__name__)


def run_cycle():
    """Distinguish a skipped lease from an executed, possibly degraded run."""
    from source_registry import active_sources
    started = time.time()
    with db.collection_lease() as acquired:
        if not acquired:
            return {"status": "skipped", "reason": "collection_already_running"}
        events = scraper.scrape_sources()
    urls = {s["canal"] for s in active_sources()}
    checked = [s for s in db.source_status() if s["url"] in urls and s["timestamp"] >= started]
    failed = [s["url"] for s in checked if s["status"] == "error"]
    incomplete = [s["url"] for s in checked if s["status"] == "needs_adapter"]
    partial = [s["url"] for s in checked if s["status"] == "partial"]
    return {"status": "degraded" if failed or incomplete or partial or len(checked) < len(urls) else "ok",
            "finished_at": datetime.now(TZ).isoformat(),
            "duration_seconds": round(time.time()-started, 2),
            "sources_checked": len(checked), "sources_expected": len(urls),
            "errors": failed, "needs_adapter": incomplete, "partial": partial,
            "collected": len(events), "public": len(db.list_public_events())}


def serve(interval, stop, cycle=run_cycle):
    """Start immediately; avoid rapid retry loops after a failing pass."""
    if interval < 60:
        raise ValueError("L'intervalle doit être d'au moins 60 secondes")
    while not stop.is_set():
        try:
            result = cycle()
            log.info("Collection cycle %s", json.dumps(result, ensure_ascii=False))
        except Exception:
            log.exception("Collection cycle failed; next scheduled cycle remains enabled")
        # An interruptible wait, measured after completion, avoids overlap
        # and catch-up storms when a slow source delays a cycle.
        stop.wait(interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Une passe, sans processus permanent")
    parser.add_argument("--interval", type=int, default=config.SCRAPE_INTERVAL_SECONDS)
    args = parser.parse_args()
    if args.interval < 60:
        parser.error("--interval doit être >= 60 secondes")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    db.init_db()
    if args.once:
        result = run_cycle()
        print(json.dumps(result, ensure_ascii=False))
        return 1 if result["status"] == "degraded" else 0
    stop = threading.Event()
    def request_stop(signum, frame):
        log.info("Arrêt demandé ; fin de la passe en cours avant fermeture")
        stop.set()
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    serve(args.interval, stop)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
