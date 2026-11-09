"""Operational alerts are deterministic and never contact external services."""
import os
import tempfile
import unittest
from pathlib import Path

from operations_report import evaluate_backup, evaluate_sources


class OperationsReportTest(unittest.TestCase):
    def source(self, *, source_id="SRC_TEST", status="ok", automatic=True):
        return {
            "source_id": source_id,
            "name": "Source synthétique",
            "url": f"https://example.test/{source_id}",
            "status": status,
            "automatic": automatic,
        }

    def successful_partial(self, *, checked_at):
        source = self.source(status="limited")
        source.update({
            "checked_at": checked_at,
            "dimensions": {
                "access_status": "ok",
                "parse_status": "ok",
                "completeness_status": "partial",
                "editorial_status": "automatic",
            },
        })
        return source

    def test_source_warning_and_critical_thresholds(self):
        now = 100 * 3600
        source = self.source()
        for age, expected in [(17.9, []), (18, ["warning"]), (24, ["critical"])]:
            with self.subTest(age=age):
                rows = [{"url": source["url"], "last_success": now - age * 3600}]
                self.assertEqual([a["level"] for a in evaluate_sources([source], rows, now)], expected)

    def test_current_error_warns_and_review_only_source_is_ignored(self):
        now = 100 * 3600
        broken = self.source(status="access_error")
        review = self.source(source_id="SRC_REVIEW", status="access_error", automatic=False)
        rows = [
            {"url": broken["url"], "last_success": now - 3600},
            {"url": review["url"], "last_success": None},
        ]
        alerts = evaluate_sources([broken, review], rows, now)
        self.assertEqual([(a["source_id"], a["level"]) for a in alerts], [("SRC_TEST", "warning")])

    def test_never_successful_automatic_source_is_critical(self):
        [alert] = evaluate_sources([self.source()], [], 100 * 3600)
        self.assertEqual((alert["level"], alert["reason"]), ("critical", "never_successful"))

    def test_three_recent_partial_readers_count_as_successes(self):
        now = 100 * 3600
        sources = []
        for source_id in ("S019", "SRC_L018", "SRC_N019"):
            source = self.successful_partial(checked_at=now - 60)
            source.update({
                "source_id": source_id,
                "name": source_id,
                "url": f"https://example.test/{source_id}",
            })
            sources.append(source)
        self.assertEqual(evaluate_sources(sources, [], now), [])

    def test_partial_run_uses_the_same_freshness_thresholds(self):
        now = 100 * 3600
        source = self.successful_partial(checked_at=now - 18 * 3600)
        [alert] = evaluate_sources([source], [], now)
        self.assertEqual((alert["level"], alert["reason"]), ("warning", "last_success_18h"))

    def test_failed_current_run_does_not_count_as_a_success(self):
        now = 100 * 3600
        source = self.source(status="parse_error")
        source.update({
            "checked_at": now - 60,
            "dimensions": {"access_status": "ok", "parse_status": "error"},
        })
        [alert] = evaluate_sources([source], [], now)
        self.assertEqual((alert["level"], alert["reason"]), ("critical", "never_successful"))

    def test_backup_thresholds_and_missing_backup(self):
        now = 100 * 3600
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            self.assertEqual(evaluate_backup(folder, now)[0]["reason"], "missing_backup")
            backup = folder / "samstag-20261102T000000Z.sqlite3"
            backup.touch()
            for age, expected in [(19.9, []), (20, ["warning"]), (24, ["critical"])]:
                with self.subTest(age=age):
                    timestamp = now - age * 3600
                    os.utime(backup, (timestamp, timestamp))
                    self.assertEqual([a["level"] for a in evaluate_backup(folder, now)], expected)
