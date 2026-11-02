"""Create, verify and retain consistent SQLite backups."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATABASE = Path("/var/lib/samstag/samstag.sqlite3")
DEFAULT_BACKUP_DIR = Path("/var/lib/samstag/backups")


def readonly_uri(path: Path) -> str:
    return path.resolve().as_uri() + "?mode=ro"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def database_summary(path: Path) -> dict:
    with sqlite3.connect(readonly_uri(path), uri=True) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )]
        counts = {}
        for table in tables:
            quoted = table.replace('"', '""')
            counts[table] = connection.execute(f'SELECT COUNT(*) FROM "{quoted}"').fetchone()[0]
    return {"integrity": integrity, "counts": counts}


def prune_backups(folder: Path, keep: int) -> list[str]:
    if keep < 1:
        raise ValueError("La rétention doit conserver au moins une sauvegarde.")
    removed = []
    for old in sorted(folder.glob("samstag-*.sqlite3"), reverse=True)[keep:]:
        old.unlink()
        removed.append(old.name)
    return removed


def create_backup(database: Path, folder: Path, keep: int = 7) -> dict:
    database = Path(database).expanduser().resolve()
    folder = Path(folder).expanduser().resolve()
    if not database.is_file():
        raise FileNotFoundError(f"Base introuvable : {database}")
    folder.mkdir(mode=0o750, parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = folder / f"samstag-{stamp}.sqlite3"
    try:
        with sqlite3.connect(readonly_uri(database), uri=True) as source:
            with sqlite3.connect(target) as copy:
                source.backup(copy)
        target.chmod(0o640)
        summary = database_summary(target)
        if summary["integrity"] != "ok":
            raise RuntimeError(f"Sauvegarde invalide : {summary['integrity']}")
        removed = prune_backups(folder, keep)
        return {
            "backup": str(target),
            "bytes": target.stat().st_size,
            "sha256": file_sha256(target),
            **summary,
            "retention": keep,
            "removed": removed,
        }
    except Exception:
        target.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Sauvegarde SQLite cohérente de Samstag")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    parser.add_argument("--keep", type=int, default=7)
    args = parser.parse_args()
    print(json.dumps(create_backup(args.database, args.backup_dir, args.keep), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
