"""Backup and restore exercises use only disposable SQLite files."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import db
from deploy.infomaniak.backup import create_backup, prune_backups
from deploy.infomaniak.restore_check import restore_backup


class BackupRestoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "source.sqlite3"
        self.db_patch = patch.object(db, "DB_PATH", str(self.source))
        self.db_patch.start()
        db.init_db()
        db.bulk_upsert([{
            "id": "synthetic-backup-event",
            "title": "Événement synthétique de restauration",
            "date": "2099-01-01",
            "time": "20:00",
        }], source="synthetic")

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def test_backup_restore_integrity_counts_and_application_read(self):
        result = create_backup(self.source, self.root / "backups with spaces", keep=7)
        backup = Path(result["backup"])
        self.assertEqual(result["integrity"], "ok")
        self.assertEqual(result["counts"]["events"], 1)
        self.assertEqual(backup.stat().st_mode & 0o777, 0o640)

        restored = self.root / "restore" / "samstag-restored.sqlite3"
        restored_result = restore_backup(backup, restored)
        self.assertEqual(restored_result["integrity"], "ok")
        self.assertEqual(restored_result["counts"], result["counts"])
        self.assertEqual(restored.stat().st_mode & 0o777, 0o640)
        with patch.object(db, "DB_PATH", str(restored)):
            events = db.list_all_events()
        self.assertEqual([row["id"] for row in events], ["synthetic-backup-event"])

    def test_restore_refuses_to_overwrite_any_existing_file(self):
        backup = Path(create_backup(self.source, self.root / "backups")["backup"])
        destination = self.root / "already-there.sqlite3"
        destination.write_text("ne pas remplacer")
        with self.assertRaises(FileExistsError):
            restore_backup(backup, destination)
        self.assertEqual(destination.read_text(), "ne pas remplacer")

    def test_retention_removes_only_old_matching_backups(self):
        folder = self.root / "backups"
        folder.mkdir()
        for index in range(4):
            (folder / f"samstag-2026010{index}T000000Z.sqlite3").touch()
        unrelated = folder / "keep-me.txt"
        unrelated.touch()
        removed = prune_backups(folder, keep=2)
        self.assertEqual(len(removed), 2)
        self.assertEqual(len(list(folder.glob("samstag-*.sqlite3"))), 2)
        self.assertTrue(unrelated.exists())
