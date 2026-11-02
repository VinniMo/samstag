"""Explain measured overlap, never a claim of exhaustive platform coverage."""
from collections import defaultdict

import db
from collection_quality import assess
from source_registry import source_for


def coverage():
    eligible = {i["event"]["id"] for i in db.collection_items()
                if i["status"] in {"candidate", "approved"}
                and assess(i["event"], i["event"]["source_url"])["status"] == "candidate"}
    with db.get_conn() as conn:
        rows = conn.execute("SELECT event_id,source_url,payload,status FROM collection_observations WHERE status!='superseded'").fetchall()
    import json
    groups = defaultdict(lambda: {"official": [], "aggregator": [], "event": {}})
    for row in rows:
        if row["event_id"] not in eligible:
            continue
        source = source_for(row["source_url"])
        if not source:
            continue
        group = groups[row["event_id"]]
        kind = source["type"]
        group[kind].append(row["source_url"])
        group["event"] = json.loads(row["payload"])
    result = {"both": [], "official_only_in_this_run": [], "aggregator_only_in_this_run": []}
    for key, group in groups.items():
        event = group["event"]
        entry = {k: event.get(k, "") for k in ["title", "date", "time", "location", "evidence_url"]}
        entry.update(id=key, official=group["official"], aggregator=group["aggregator"])
        bucket = "both" if group["official"] and group["aggregator"] else "official_only_in_this_run" if group["official"] else "aggregator_only_in_this_run"
        result[bucket].append(entry)
    return {"method": "Exact title + canonical venue + date + time in collected observations. No overall coverage percentage; detail limits and different titles/hours can prevent matches.", **result}


def duplicate_candidates(items=None):
    """Report different records sharing one verified venue, date and time.

    This first L3 pass is deliberately read-only. It does not decide whether two
    records describe the same event and never changes stored observations.
    """
    items = db.collection_items() if items is None else items
    slots = defaultdict(list)
    for item in items:
        if item.get("status") not in {"candidate", "approved"}:
            continue
        event = item.get("event", {})
        key = (event.get("venue_id", ""), event.get("date", ""), event.get("time", ""))
        if not all(key):
            continue
        source_url = event.get("source_url", "")
        source = source_for(source_url) or {}
        evidence = []
        for url in [*item.get("evidence_urls", []), event.get("evidence_url"), source_url]:
            if url and url not in evidence:
                evidence.append(url)
        slots[key].append({
            "id": event.get("id", ""),
            "title": event.get("title", ""),
            "location": event.get("location", ""),
            "source_url": source_url,
            "source_name": source.get("nom", ""),
            "source_type": source.get("type", "unknown"),
            "status": item.get("status", ""),
            "evidence_urls": evidence,
        })

    candidates = []
    for (venue_id, date, time), records in sorted(slots.items()):
        unique_ids = {record["id"] for record in records}
        if len(unique_ids) < 2:
            continue
        records.sort(key=lambda record: (record["source_type"] != "official", record["title"], record["id"]))
        source_types = sorted({record["source_type"] for record in records})
        candidates.append({
            "candidate_key": f"{venue_id}|{date}|{time}",
            "venue_id": venue_id,
            "date": date,
            "time": time,
            "location": next((record["location"] for record in records if record["location"]), ""),
            "classification": "official_and_aggregator" if {"official", "aggregator"}.issubset(source_types) else "same_slot_review",
            "records": records,
        })

    return {
        "method": "Different records with the same canonical venue, date and explicit time. Read-only: every candidate still requires a later identity decision.",
        "summary": {
            "candidate_groups": len(candidates),
            "candidate_records": sum(len(group["records"]) for group in candidates),
            "official_and_aggregator_groups": sum(group["classification"] == "official_and_aggregator" for group in candidates),
            "review_groups": sum(group["classification"] == "same_slot_review" for group in candidates),
        },
        "candidates": candidates,
    }
