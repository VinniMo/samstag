"""Flask application entry point — routes and bootstrap."""
from __future__ import annotations

import logging
import os
import secrets
import threading
import time
from collections import Counter
from datetime import datetime

from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS

import agenda
import db
import scraper
from config import config
from seed_data import build_demo_events
from source_registry import source_for

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


DEMO_SOURCE = "seed"


def ensure_demo_events() -> None:
    """Keep the fictional demo programme dated from today.

    Demo events are only written when no collected event exists, and are
    rewritten once a day so the page never shows a stale, all-past demo.
    """
    if not config.DEMO_ENABLED or db.list_public_events():
        return
    today = agenda.today_local()
    written = db.oldest_update(DEMO_SOURCE)
    if written and agenda.today_local(datetime.fromtimestamp(written, agenda.TZ)) == today:
        return
    db.delete_source(DEMO_SOURCE)
    events = build_demo_events(today)
    db.bulk_upsert(events, source=DEMO_SOURCE)
    logger.info("Wrote %d demo events dated from %s", len(events), today)


def bootstrap_database() -> None:
    """Initialize schema and make sure there is something to show."""
    db.init_db()
    ensure_demo_events()


_refresh_lock = threading.Lock()


def _refresh_in_background() -> None:
    try:
        count = scraper.refresh_database()
        logger.info("Scraper refresh produced %d events", count)
    except Exception:
        logger.exception("Scraper refresh failed; falling back to existing data")
    finally:
        _refresh_lock.release()


def maybe_refresh_from_scraper() -> None:
    """Start a collection in the background when the last attempt is old.

    Visitors are served the data already stored; they never wait for the
    sources. Any attempt counts, so failing sources are retried at most
    once per interval rather than on every page view.
    """
    if not config.COLLECTION_ON_VISIT:
        return
    age = time.time() - db.last_scrape_time()
    if age < config.SCRAPE_INTERVAL_SECONDS:
        return
    if not _refresh_lock.acquire(blocking=False):
        return  # a collection is already running in this process
    threading.Thread(target=_refresh_in_background, daemon=True).start()


def _check_auth(username: str, password: str) -> bool:
    expected_user = os.environ.get("BASIC_AUTH_USER", "")
    expected_pass = os.environ.get("BASIC_AUTH_PASS", "")
    return (
        secrets.compare_digest(username, expected_user)
        and secrets.compare_digest(password, expected_pass)
    )


def _auth_required_response() -> Response:
    return Response(
        "Authentification requise.\n", 401,
        {"WWW-Authenticate": 'Basic realm="Lausanne Cultura"'},
    )


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.secret_key = os.environ.get('CULTURA_SESSION_SECRET') or secrets.token_hex(32)
    app.config.update(MAX_CONTENT_LENGTH=16_384, SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE='Lax',
                      SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1')
    CORS(app, resources={r'/api/(events|categories|health|sources)$': {'origins': '*', 'methods': ['GET']}})

    bootstrap_database()
    from feedback import feedback, init_feedback
    init_feedback()
    app.register_blueprint(feedback)

    auth_enabled = bool(
        os.environ.get("BASIC_AUTH_USER") and os.environ.get("BASIC_AUTH_PASS")
    )

    @app.before_request
    def gate():
        if not auth_enabled:
            return None
        if request.path == "/api/health":
            return None
        creds = request.authorization
        if not creds or not _check_auth(creds.username or "", creds.password or ""):
            return _auth_required_response()
        return None

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    @app.route("/api/events")
    def api_events():
        maybe_refresh_from_scraper()
        ensure_demo_events()
        search = request.args.get("search", "").strip()

        # Collected events win; demo events only show when nothing was collected.
        events = db.list_public_events()
        demo = config.DEMO_ENABLED and not events
        if demo:
            events = [e for e in db.list_all_events() if e["source"] == DEMO_SOURCE]
        if search:
            events = [e for e in events if agenda.matches(e, search)]

        programme = (agenda.build_programme(events, agenda.today_local()) if demo
                     else agenda.build_night_programme(events))
        last = db.last_scrape_time(successful_only=True)
        return jsonify({
            **programme,
            "search": search,
            "total": len(programme["events"]),
            "demo": demo,
            "rubrics": list(agenda.RUBRIC_ORDER),
            "small_price_chf": agenda.SMALL_PRICE_CHF,
            "last_update": datetime.fromtimestamp(last, agenda.TZ).isoformat() if last else None,
            "source_count": len(config.SCRAPE_SOURCES),
        })

    @app.route("/api/categories")
    def api_categories():
        counts = Counter(e["category"] for e in db.list_public_events())
        return jsonify({
            "categories": [{"name": name, "count": count} for name, count in counts.items()],
            "all": list(config.CATEGORIES),
        })

    @app.route("/api/refresh", methods=["POST", "GET"])
    def api_refresh():
        try:
            count = scraper.refresh_database()
            return jsonify({
                "ok": True,
                "scraped": count,
                "total": len(db.list_public_events()),
                "pending": sum(i["status"] in {"candidate", "review"} for i in db.collection_items()),
            })
        except Exception as exc:
            logger.exception("Manual refresh failed")
            return jsonify({"ok": False, "error": str(exc)}), 500

    @app.route("/api/sources")
    def api_sources():
        """Which sources answer and how many events each one gives."""
        latest = {row["url"]: row for row in db.source_status()}
        items = db.collection_items()
        public_events = db.list_public_events()
        sources = []
        for url in config.SCRAPE_SOURCES:
            source = source_for(url)
            row = latest.get(url)
            stages = [i for i in items if i["event"].get("source_url") == url]
            sources.append({
                "url": url,
                "venue_id": source["venue_id"] if source else None,
                "venue": source["nom"] if source else None,
                "publication": "automatique après contrôles" if source and source["auto_publish"] else "validation requise",
                "candidates": sum(i["status"] == "candidate" for i in stages),
                "to_review": sum(i["status"] == "review" for i in stages),
                "excluded": sum(i["status"] == "excluded" for i in stages),
                "public_events": sum(e.get("source_url") == url for e in public_events),
                "research_note": source["notes"] if source else "",
                "status": row["status"] if row else "jamais collectée",
                "events": row["count"] if row else 0,
                "detail": row["message"] if row else "",
                "checked_at": (
                    datetime.fromtimestamp(row["timestamp"], agenda.TZ).isoformat(timespec="minutes")
                    if row else None
                ),
                "last_success_at": (
                    datetime.fromtimestamp(row["last_success"], agenda.TZ).isoformat(timespec="minutes")
                    if row and row.get("last_success") else None
                ),
            })
        working = sum(1 for s in sources if s["status"] == "ok")
        return jsonify({
            "summary": f"{working} source(s) sur {len(sources)} livrent des entrées ; {len(public_events)} sortie(s) validée(s) affichable(s)",
            "sources": sorted(sources, key=lambda s: (s["status"] != "ok", -s["events"], s["url"])),
        })

    @app.route("/api/health")
    def api_health():
        from collection_health import health
        return jsonify({
            "status": "ok",
            "events_in_db": len(db.collection_items()),
            "legacy_events": db.count_events(),
            "public_events": len(db.list_public_events()),
            "collection_items": len(db.collection_items()),
            "last_scrape": db.last_scrape_time(),
            "collection": health(),
        })

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_err):
        return jsonify({"error": "internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
