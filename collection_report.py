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
