"""Verify a prepared Samstag release directory without changing it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_release(root: Path) -> dict:
    root = Path(root).resolve()
    checksum_file = root / "SHA256SUMS"
    if not checksum_file.is_file():
        raise FileNotFoundError(f"Manifeste absent : {checksum_file}")

    checked = []
    for number, raw in enumerate(checksum_file.read_text().splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            expected, relative = raw.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"Ligne d'empreinte invalide : {number}") from exc
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"Chemin interdit dans le manifeste : {relative}")
        target = root / candidate
        if not target.is_file():
            raise FileNotFoundError(f"Fichier absent : {relative}")
        actual = file_sha256(target)
        if actual != expected:
            raise ValueError(f"Empreinte différente : {relative}")
        checked.append(relative)

    if not checked:
        raise ValueError("Le manifeste d'empreintes est vide.")
    return {"status": "ok", "root": str(root), "files_checked": len(checked)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Dossier de livraison extrait")
    args = parser.parse_args()
    print(json.dumps(verify_release(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
