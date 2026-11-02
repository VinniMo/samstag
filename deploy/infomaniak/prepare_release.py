"""Build a traceable Samstag release archive from a reviewed Git commit."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    from .verify_release import file_sha256, verify_release
except ImportError:  # Direct execution from this directory.
    from verify_release import file_sha256, verify_release


ROOT_FILES = {"requirements.lock", "requirements.txt"}
RUNTIME_PREFIXES = ("data/", "samstag/", "static/", "templates/")
DEPLOY_FILES = {
    "deploy/infomaniak/backup.py",
    "deploy/infomaniak/restore_check.py",
    "deploy/infomaniak/verify_release.py",
}


def git(repo: Path, *args: str, text: bool = True):
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=text, stderr=subprocess.DEVNULL
    )


def release_paths(paths: list[str]) -> list[str]:
    selected = []
    for path in paths:
        if "/" not in path and path.endswith(".py"):
            selected.append(path)
        elif path in ROOT_FILES or path in DEPLOY_FILES:
            selected.append(path)
        elif path.startswith(RUNTIME_PREFIXES):
            selected.append(path)
    return sorted(selected)


def tracked_paths(repo: Path, commit: str) -> list[str]:
    output = git(repo, "ls-tree", "-r", "--name-only", "-z", commit)
    return [path for path in output.split("\0") if path]


def write_commit_file(repo: Path, commit: str, relative: str, destination: Path) -> None:
    content = git(repo, "show", f"{commit}:{relative}", text=False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    destination.chmod(0o644)


def build_release(repo: Path, output_dir: Path, revision: str = "HEAD") -> dict:
    repo = Path(repo).resolve()
    output_dir = Path(output_dir).resolve()
    commit = git(repo, "rev-parse", f"{revision}^{{commit}}").strip()
    short = commit[:12]
    paths = release_paths(tracked_paths(repo, commit))
    if not paths:
        raise ValueError("Aucun fichier d'exécution trouvé dans le commit.")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"samstag-{short}.tar.gz"
    sidecar = output_dir / f"{archive.name}.sha256"
    with tempfile.TemporaryDirectory(prefix="samstag-release-") as temporary:
        release_root = Path(temporary) / f"samstag-{short}"
        release_root.mkdir()
        for relative in paths:
            write_commit_file(repo, commit, relative, release_root / relative)

        metadata = {
            "project": "Samstag",
            "commit": commit,
            "commit_short": short,
            "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "payload_files": len(paths),
            "database": "external SQLite file; never included",
        }
        (release_root / "RELEASE.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
        )
        checksummed = paths + ["RELEASE.json"]
        lines = [
            f"{file_sha256(release_root / relative)}  {relative}"
            for relative in sorted(checksummed)
        ]
        (release_root / "SHA256SUMS").write_text("\n".join(lines) + "\n")
        verify_release(release_root)

        temporary_archive = Path(temporary) / archive.name
        with tarfile.open(temporary_archive, "w:gz") as bundle:
            bundle.add(release_root, arcname=release_root.name)
        shutil.move(temporary_archive, archive)

    archive_hash = file_sha256(archive)
    sidecar.write_text(f"{archive_hash}  {archive.name}\n")
    return {
        "archive": str(archive),
        "archive_sha256": archive_hash,
        "commit": commit,
        "files": len(paths),
        "checksum_file": str(sidecar),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path, default=Path(".artifacts/releases"))
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    print(json.dumps(build_release(args.repo, args.output_dir, args.revision), indent=2))


if __name__ == "__main__":
    main()
