"""Administrative routes must fail closed without contacting real sources."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import db


class ManualRefreshSecurityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(db, "DB_PATH", str(Path(self.tmp.name) / "security.sqlite3"))
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def client(self, *, enabled="0", token=""):
        environment = {
            "MANUAL_REFRESH_ENABLED": enabled,
            "SAMSTAG_REFRESH_TOKEN": token,
            "BASIC_AUTH_USER": "",
            "BASIC_AUTH_PASS": "",
        }
        with patch.dict(os.environ, environment):
            web = app.create_app()
        web.config["TESTING"] = True
        return web.test_client()

    def test_manual_refresh_is_disabled_by_default(self):
        with patch.object(app.scraper, "refresh_database") as refresh:
            client = self.client()
            self.assertEqual(client.post("/api/refresh").status_code, 404)
            self.assertEqual(client.get("/api/refresh").status_code, 405)
            refresh.assert_not_called()

    def test_enabled_route_rejects_missing_short_or_wrong_secret(self):
        valid = "v" * 32
        with patch.object(app.scraper, "refresh_database") as refresh:
            self.assertEqual(self.client(enabled="1").post("/api/refresh").status_code, 404)
            self.assertEqual(
                self.client(enabled="1", token="short").post(
                    "/api/refresh", headers={"X-Samstag-Refresh-Token": "short"}
                ).status_code,
                404,
            )
            self.assertEqual(
                self.client(enabled="1", token=valid).post(
                    "/api/refresh", headers={"X-Samstag-Refresh-Token": "wrong"}
                ).status_code,
                403,
            )
            refresh.assert_not_called()

    def test_enabled_route_accepts_only_the_dedicated_secret(self):
        valid = "v" * 32
        with patch.object(app.scraper, "refresh_database", return_value=3) as refresh:
            response = self.client(enabled="1", token=valid).post(
                "/api/refresh", headers={"X-Samstag-Refresh-Token": valid}
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()["ok"])
            refresh.assert_called_once_with()
