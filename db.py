"""SQLite persistence layer for Lausanne Cultura events."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
import threading
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Iterator

from config import config

DB_PATH = config.DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    date        TEXT,
    time        TEXT,
    end_date    TEXT,
    location    TEXT,
    address     TEXT,
    category    TEXT,
    subcategory TEXT,
    description TEXT,
    image       TEXT,
    price       TEXT,
    url         TEXT,
    tags        TEXT,
    featured    INTEGER DEFAULT 0,
    source      TEXT DEFAULT 'fallback',
    scraped_at  REAL,
    updated_at  REAL
);

CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_date     ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_featured ON events(featured);

CREATE TABLE IF NOT EXISTS scrape_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source     TEXT,
    url        TEXT,
    status     TEXT,
    count      INTEGER,
    message    TEXT,
    timestamp  REAL
);

CREATE TABLE IF NOT EXISTS collection_items (
    id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence_urls TEXT NOT NULL,
    reviewed_at REAL
);
CREATE TABLE IF NOT EXISTS collection_observations (
    source_url TEXT NOT NULL,
    event_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT NOT NULL,
    checked_at REAL NOT NULL,
    PRIMARY KEY(source_url,event_id)
);
CREATE TABLE IF NOT EXISTS collection_locks (
    name TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collection_presence (
    source_url TEXT NOT NULL,
    event_id TEXT NOT NULL,
    missing_runs INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(source_url,event_id)
);
"""


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection that auto-commits on exit and always closes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables and indexes if they don't exist."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def upsert_event(evt: dict, source: str = "scraper") -> None:
    """Insert or update an event keyed on its id."""
    now = time.time()
    tags = json.dumps(evt.get("tags", []), ensure_ascii=False)
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO events (id, title, date, time, end_date, location, address,
                                category, subcategory, description, image, price, url,
                                tags, featured, source, scraped_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title, date=excluded.date, time=excluded.time,
                end_date=excluded.end_date, location=excluded.location,
                address=excluded.address, category=excluded.category,
                subcategory=excluded.subcategory, description=excluded.description,
                image=excluded.image, price=excluded.price, url=excluded.url,
                tags=excluded.tags, featured=excluded.featured,
                source=excluded.source, updated_at=excluded.updated_at
        """, (
            evt.get("id"), evt.get("title", ""), evt.get("date", ""),
            evt.get("time", ""), evt.get("end_date", ""), evt.get("location", ""),
            evt.get("address", ""), evt.get("category", ""), evt.get("subcategory", ""),
            evt.get("description", ""), evt.get("image", ""), evt.get("price", ""),
            evt.get("url", ""), tags, 1 if evt.get("featured") else 0,
            source, now, now,
        ))


def bulk_upsert(events: list[dict], source: str = "scraper") -> None:
    """Upsert many events under the same source label."""
    for evt in events:
        upsert_event(evt, source=source)


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    try:
        d["tags"] = json.loads(d.get("tags") or "[]")
    except Exception:
        d["tags"] = []
    d["featured"] = bool(d.get("featured"))
    return d


def count_events(source: str | None = None, exclude_source: str | None = None) -> int:
    sql, params = "SELECT COUNT(*) AS n FROM events WHERE 1=1", []
    if source:
        sql += " AND source = ?"
        params.append(source)
    if exclude_source:
        sql += " AND source != ?"
        params.append(exclude_source)
    with get_conn() as conn:
        return conn.execute(sql, params).fetchone()["n"]


def list_all_events(exclude_source: str | None = None) -> list[dict]:
    sql, params = "SELECT * FROM events", []
    if exclude_source:
        sql += " WHERE source != ?"
        params.append(exclude_source)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(r) for r in rows]


def oldest_update(source: str) -> float:
    """When rows from this source were last written (0 when there are none)."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT MIN(updated_at) AS ts FROM events WHERE source = ?", (source,)
        ).fetchone()
    return row["ts"] or 0.0


def delete_source(source: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM events WHERE source = ?", (source,))


def list_categories() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, COUNT(*) AS n FROM events WHERE category != '' GROUP BY category ORDER BY n DESC"
        ).fetchall()
    return [{"name": r["category"], "count": r["n"]} for r in rows]


def log_scrape(source: str, url: str, status: str, count: int, message: str = "") -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO scrape_log (source, url, status, count, message, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (source, url, status, count, message, time.time()),
        )


def last_scrape_time(successful_only: bool = False) -> float:
    """Time of the last collection attempt (or last successful one)."""
    sql = "SELECT MAX(timestamp) AS ts FROM scrape_log"
    if successful_only:
        sql += " WHERE status = 'ok'"
    with get_conn() as conn:
        row = conn.execute(sql).fetchone()
    return row["ts"] or 0.0


def source_status() -> list[dict]:
    """Latest collection result for each source URL."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT l.url, l.status, l.count, l.message, l.timestamp,
                   (SELECT MAX(s.timestamp) FROM scrape_log s
                    WHERE s.url=l.url AND s.status IN ('ok','empty')) AS last_success
            FROM scrape_log l
            JOIN (SELECT url, MAX(id) AS id FROM scrape_log GROUP BY url) last
              ON last.id = l.id
        """).fetchall()
    return [dict(r) for r in rows]


def clear_events() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM events")


def stage_collection(item: dict) -> None:
    """Store each source's evidence and select the most authoritative fresh one."""
    from source_registry import source_for
    event = item["event"]
    with get_conn() as conn:
        conn.execute("""INSERT INTO collection_observations VALUES(?,?,?,?,?,?)
            ON CONFLICT(source_url,event_id) DO UPDATE SET payload=excluded.payload,
            status=excluded.status,reason=excluded.reason,checked_at=excluded.checked_at""",
            (event["source_url"], event["id"], json.dumps(event, ensure_ascii=False), item["status"], item["reason"], time.time()))
        # A stable key is emitted only by a reader of a one-occurrence page.
        # A feed or calendar shared by many events never uses this mechanism.
        if event.get("source_event_key"):
            previous = conn.execute("SELECT event_id,payload FROM collection_observations WHERE source_url=? AND event_id!=?",
                                    (event["source_url"], event["id"])).fetchall()
            for row in previous:
                if json.loads(row["payload"]).get("source_event_key") == event["source_event_key"]:
                    conn.execute("UPDATE collection_observations SET status='superseded',reason='changed_occurrence' WHERE source_url=? AND event_id=?",
                                 (event["source_url"], row["event_id"]))
                    conn.execute("UPDATE collection_items SET status='superseded',reason='changed_occurrence' WHERE id=?", (row["event_id"],))
        old = conn.execute("SELECT * FROM collection_items WHERE id=?", (event["id"],)).fetchone()
        evidence = json.loads(old["evidence_urls"]) if old else []
        for url in (event.get("source_url"), event.get("evidence_url")):
            if url and url not in evidence:
                evidence.append(url)
        observations = conn.execute("SELECT * FROM collection_observations WHERE event_id=? AND (checked_at>=? OR status IN ('superseded','withdrawn'))",
                                    (event["id"], time.time()-86400)).fetchall()
        def priority(row):
            source = source_for(row["source_url"])
            return ((source or {}).get("priority", 100), -row["checked_at"])
        selected = min(observations, key=priority)
        event = json.loads(selected["payload"])
        status, reason = selected["status"], selected["reason"]
        source = source_for(event["source_url"])
        if status == "candidate" and source and source.get("auto_publish"):
            status, reason = "approved", "qualified_source_complete_event"
        if old and old["status"] == "approved" and status == "candidate":
            previous = json.loads(old["payload"])
            comparable = lambda e: {k: v for k, v in e.items() if k != "checked_at"}
            if comparable(previous) == comparable(event):
                status, reason = "approved", "reviewed_unchanged"
        conn.execute("""INSERT INTO collection_items(id,payload,status,reason,evidence_urls)
            VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,
            status=excluded.status, reason=excluded.reason, evidence_urls=excluded.evidence_urls""",
            (event["id"], json.dumps(event, ensure_ascii=False), status, reason, json.dumps(evidence)))


def collection_items() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM collection_items ORDER BY id").fetchall()
    return [{"event": json.loads(r["payload"]), "status": r["status"], "reason": r["reason"],
             "evidence_urls": json.loads(r["evidence_urls"])} for r in rows]


def reconcile_source_snapshot(source_url: str, seen_ids: set[str]) -> None:
    """Withdraw only after two consecutive successful, complete snapshots.

    Partial listings, request failures and capped pagination never call this.
    A disappearance is not labelled cancellation: the reason remains explicit.
    """
    with get_conn() as conn:
        rows = conn.execute("SELECT event_id FROM collection_observations WHERE source_url=?", (source_url,)).fetchall()
        for row in rows:
            event_id = row["event_id"]
            if event_id in seen_ids:
                conn.execute("INSERT INTO collection_presence VALUES(?,?,0) ON CONFLICT(source_url,event_id) DO UPDATE SET missing_runs=0", (source_url,event_id))
                continue
            # The provider's upcoming-only view may legitimately omit an event
            # after it starts. That absence is not evidence of withdrawal.
            original = conn.execute("SELECT payload FROM collection_observations WHERE source_url=? AND event_id=?", (source_url,event_id)).fetchone()
            try:
                start = datetime.fromisoformat(json.loads(original["payload"])["start_at"].replace("Z", "+00:00"))
                if start.tzinfo and start.timestamp() <= time.time():
                    continue
            except (ValueError, KeyError, TypeError):
                continue
            conn.execute("INSERT INTO collection_presence VALUES(?,?,1) ON CONFLICT(source_url,event_id) DO UPDATE SET missing_runs=missing_runs+1", (source_url,event_id))
            missing = conn.execute("SELECT missing_runs FROM collection_presence WHERE source_url=? AND event_id=?", (source_url,event_id)).fetchone()["missing_runs"]
            if missing < 2:
                continue
            conn.execute("UPDATE collection_observations SET status='withdrawn',reason='absent_two_complete_snapshots' WHERE source_url=? AND event_id=?", (source_url,event_id))
            current = conn.execute("SELECT payload FROM collection_items WHERE id=?", (event_id,)).fetchone()
            if current and json.loads(current["payload"]).get("source_url") == source_url:
                conn.execute("UPDATE collection_items SET status='withdrawn',reason='absent_two_complete_snapshots' WHERE id=?", (event_id,))


def approve_collection(event_id: str) -> None:
    from collection_quality import publicly_visible
    item = next((i for i in collection_items() if i["event"]["id"] == event_id), None)
    if not item or item["status"] != "candidate":
        raise ValueError("Seul un candidat complet peut être validé.")
    item["status"] = "approved"
    if not publicly_visible(item):
        raise ValueError("Événement périmé ou incomplet : relancer la collecte.")
    with get_conn() as conn:
        conn.execute("UPDATE collection_items SET status='approved',reason='reviewed',reviewed_at=? WHERE id=?",
                     (time.time(), event_id))


def list_public_events() -> list[dict]:
    from collection_quality import publicly_visible
    return [{**i["event"], "evidence_urls": i["evidence_urls"]} for i in collection_items() if publicly_visible(i)]


@contextmanager
def collection_lease(ttl: int = 1800):
    """SQLite lease shared across Gunicorn processes and the local CLI."""
    owner = uuid.uuid4().hex
    now = time.time()
    with get_conn() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM collection_locks WHERE name='refresh' AND expires_at<=?", (now,))
        inserted = conn.execute("INSERT OR IGNORE INTO collection_locks VALUES('refresh',?,?)", (owner, now+ttl)).rowcount
    stop = threading.Event()
    def renew():
        while not stop.wait(min(30, max(0.05, ttl/3))):
            try:
                with get_conn() as conn:
                    conn.execute("UPDATE collection_locks SET expires_at=? WHERE name='refresh' AND owner=?", (time.time()+ttl, owner))
            except sqlite3.Error:
                logging.getLogger(__name__).exception("Could not renew collection lease")
    heartbeat = threading.Thread(target=renew, daemon=True) if inserted else None
    if heartbeat:
        heartbeat.start()
    try:
        yield bool(inserted)
    finally:
        if inserted:
            stop.set()
            heartbeat.join(timeout=1)
            with get_conn() as conn:
                conn.execute("DELETE FROM collection_locks WHERE name='refresh' AND owner=?", (owner,))
