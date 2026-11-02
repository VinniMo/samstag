import tempfile
import unittest
from pathlib import Path

from deploy.infomaniak.prepare_release import release_paths
from deploy.infomaniak.verify_release import file_sha256, verify_release


class ReleasePreparationTests(unittest.TestCase):
    def test_runtime_selection_excludes_private_and_development_files(self):
        selected = release_paths([
            "app.py",
            "requirements.lock",
            "data/sources.json",
            "samstag/collection/adapters/vidy.py",
            "static/js/main.js",
            "templates/index.html",
            "deploy/infomaniak/backup.py",
            "deploy/infomaniak/verify_release.py",
            "tests/test_app_security.py",
            "docs/EXPLOITATION.md",
            "e2e/server.py",
            ".env",
        ])
        self.assertEqual(selected, [
            "app.py",
            "data/sources.json",
            "deploy/infomaniak/backup.py",
            "deploy/infomaniak/verify_release.py",
            "requirements.lock",
            "samstag/collection/adapters/vidy.py",
            "static/js/main.js",
            "templates/index.html",
        ])

    def test_verifier_detects_a_modified_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = root / "app.py"
            payload.write_text("safe\n")
            (root / "SHA256SUMS").write_text(f"{file_sha256(payload)}  app.py\n")
            self.assertEqual(verify_release(root)["files_checked"], 1)
            payload.write_text("changed\n")
            with self.assertRaisesRegex(ValueError, "Empreinte différente"):
                verify_release(root)


if __name__ == "__main__":
    unittest.main()
