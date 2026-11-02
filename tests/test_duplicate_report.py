"""L3 read-only duplicate candidate reporting."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db
import agenda
import collection_quality as quality
from collection_report import duplicate_candidates
from datetime import datetime, timedelta


FIXTURE = Path(__file__).parent / "fixtures" / "l3_mike_d.json"


class DuplicateReportTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path_patch = patch.object(db, "DB_PATH", str(Path(self.directory.name) / "l3.sqlite3"))
        self.path_patch.start()
        db.init_db()

    def tearDown(self):
        self.path_patch.stop()
        self.directory.cleanup()

    def insert_items(self, items):
        with db.get_conn() as conn:
            for item in items:
                event = item["event"]
                conn.execute(
                    "INSERT INTO collection_items(id,payload,status,reason,evidence_urls) VALUES(?,?,?,?,?)",
                    (event["id"], json.dumps(event), item["status"], item["reason"], json.dumps(item["evidence_urls"])),
                )

    def test_mike_d_is_reported_without_changing_the_isolated_database(self):
        items = json.loads(FIXTURE.read_text())["items"]
        self.insert_items(items)
        before = db.collection_items()

        report = duplicate_candidates()

        self.assertEqual(db.collection_items(), before)
        self.assertEqual(report["summary"], {
            "candidate_groups": 1,
            "candidate_records": 2,
            "safe_match_groups": 1,
            "review_groups": 0,
        })
        [candidate] = report["candidates"]
        self.assertEqual(candidate["candidate_key"], "L001|2026-11-03|20:30")
        self.assertEqual([row["title"] for row in candidate["records"]], ["Mike D 5D", "Mike D"])
        self.assertEqual({row["source_type"] for row in candidate["records"]}, {"official", "aggregator"})
        self.assertEqual(candidate["decision"], "safe_match")
        self.assertEqual(candidate["canonical_id"], "mike-d-official")

    def test_same_slot_is_only_reported_and_incomplete_slots_are_ignored(self):
        base = json.loads(FIXTURE.read_text())["items"][0]
        items = [
            base,
            {**base, "event": {**base["event"], "id": "distinct-show", "title": "Spectacle distinct",
                                "source_url": "https://www.docks.ch/programme/",
                                "evidence_url": "https://www.docks.ch/evenement/distinct/"}},
            {**base, "event": {**base["event"], "id": "unknown-time", "title": "Horaire inconnu", "time": ""}},
        ]
        self.insert_items(items)

        report = duplicate_candidates()

        self.assertEqual(report["summary"]["review_groups"], 1)
        self.assertEqual(report["summary"]["candidate_groups"], 1)
        self.assertEqual(len(db.collection_items()), 3)
        self.assertEqual({row["title"] for row in report["candidates"][0]["records"]},
                         {"Mike D 5D", "Spectacle distinct"})
        self.assertEqual(report["candidates"][0]["decision"], "review_required")

    def test_safe_match_prefers_official_preserves_proofs_and_is_reversible(self):
        start = (datetime.now(agenda.TZ) + timedelta(days=1)).replace(hour=20, minute=30, second=0, microsecond=0)
        common = {
            "location": "Les Docks", "municipality": "Lausanne", "event_kind": "MusicEvent",
            "date": start.date().isoformat(), "time": "20:30", "start_at": start.isoformat(),
            "event_status": "EventScheduled",
        }
        official_url = "https://www.docks.ch/evenement/concerts/test/mike-d-5d/"
        aggregator_url = "https://www.l-agenda.ch/evenements/mike-d/"
        db.stage_collection(quality.assess(
            {**common, "title": "Mike D 5D", "evidence_url": official_url, "url": official_url},
            "https://www.docks.ch/programme/",
        ))
        db.stage_collection(quality.assess(
            {**common, "title": "Mike D", "evidence_url": aggregator_url, "url": aggregator_url},
            "https://www.l-agenda.ch/evenements/",
        ))
        self.assertEqual(len(db.list_public_events()), 2)
        before = db.collection_items()

        result = db.apply_safe_duplicate_matches()

        self.assertEqual(result, {"matched_groups": 1, "matched_records": 1, "review_groups": 0})
        [published] = db.list_public_events()
        self.assertEqual(published["title"], "Mike D 5D")
        self.assertEqual(published["source_url"], "https://www.docks.ch/programme/")
        self.assertIn(official_url, published["evidence_urls"])
        self.assertIn(aggregator_url, published["evidence_urls"])
        self.assertEqual(db.collection_items(), before)
        [match] = db.duplicate_matches()
        self.assertEqual(match["canonical_id"], published["id"])

        self.assertTrue(db.undo_duplicate_match(match["member_id"]))
        self.assertEqual(len(db.list_public_events()), 2)
        self.assertEqual(len(db.duplicate_matches()), 0)
        self.assertEqual(len(db.duplicate_matches(active_only=False)), 1)

        db.apply_safe_duplicate_matches()
        self.assertEqual(len(db.duplicate_matches()), 1)
        db.apply_safe_duplicate_matches({"candidates": [], "summary": {"review_groups": 0}})
        self.assertEqual(len(db.list_public_events()), 2)
        self.assertEqual(len(db.duplicate_matches()), 0)

    def test_title_mismatch_or_competing_official_record_stays_separate(self):
        items = json.loads(FIXTURE.read_text())["items"]
        mismatch = [{**item, "event": {**item["event"]}} for item in items]
        mismatch[1]["event"]["title"] = "Spectacle distinct"
        report = duplicate_candidates(mismatch)
        self.assertEqual(report["summary"], {
            "candidate_groups": 1, "candidate_records": 2,
            "safe_match_groups": 0, "review_groups": 1,
        })
        self.assertEqual(db.apply_safe_duplicate_matches(report),
                         {"matched_groups": 0, "matched_records": 0, "review_groups": 1})
        self.assertEqual(db.duplicate_matches(), [])


if __name__ == "__main__":
    unittest.main()
