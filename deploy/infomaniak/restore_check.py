"""Restore a SQLite backup to a new isolated file and verify it."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

try:
    from .backup import database_summary, file_sha256, readonly_uri
except ImportError:  # Direct execution on the server.
    from backup import database_summary, file_sha256, readonly_uri


def restore_backup(backup: Path, destination: Path) -> dict:
    backup = Path(backup).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()
    if not backup.is_file():
        raise FileNotFoundError(f"Sauvegarde introuvable : {backup}")
    if destination.exists():
        raise FileExistsError(f"La destination existe déjà : {destination}")
    if backup == destination:
        raise ValueError("La restauration doit utiliser un nouveau fichier isolé.")
    destination.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
    try:
        with sqlite3.connect(readonly_uri(backup), uri=True) as source:
            with sqlite3.connect(destination) as restored:
                source.backup(restored)
        destination.chmod(0o640)
        summary = database_summary(destination)
        if summary["integrity"] != "ok":
            raise RuntimeError(f"Restauration invalide : {summary['integrity']}")
        return {
            "restored": str(destination),
            "bytes": destination.stat().st_size,
            "sha256": file_sha256(destination),
            **summary,
        }
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Restauration isolée et vérifiée de Samstag")
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(restore_backup(args.backup, args.destination), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
