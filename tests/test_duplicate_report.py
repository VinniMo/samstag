"""L3 read-only duplicate candidate reporting."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db
from collection_report import duplicate_candidates


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
            "official_and_aggregator_groups": 1,
            "review_groups": 0,
        })
        [candidate] = report["candidates"]
        self.assertEqual(candidate["candidate_key"], "L001|2026-11-03|20:30")
        self.assertEqual([row["title"] for row in candidate["records"]], ["Mike D 5D", "Mike D"])
        self.assertEqual({row["source_type"] for row in candidate["records"]}, {"official", "aggregator"})

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


if __name__ == "__main__":
    unittest.main()
