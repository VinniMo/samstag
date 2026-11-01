#!/usr/bin/env python3
"""Validate Samstag JSON registries against schemas and cross references."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REGISTRIES = ("sources", "venues", "bars")


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: JSON invalide: {exc}") from exc


def validate_registry(name: str):
    data_path = ROOT / "data" / f"{name}.json"
    schema_path = ROOT / "schemas" / f"{name}.schema.json"
    data, schema = load(data_path), load(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        messages = []
        for error in errors:
            location = "/".join(map(str, error.absolute_path)) or "racine"
            messages.append(f"{data_path.relative_to(ROOT)}:{location}: {error.message}")
        raise ValueError("\n".join(messages))
    ids = [item["id"] for item in data]
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise ValueError(f"{data_path.relative_to(ROOT)}: identifiants dupliqués: {', '.join(duplicates)}")
    return data


def main() -> int:
    try:
        sources, venues, bars = (validate_registry(name) for name in REGISTRIES)
        venue_ids = {venue["id"] for venue in venues}
        unknown_sources = sorted({source["venue_id"] for source in sources if source["venue_id"]} - venue_ids)
        if unknown_sources:
            raise ValueError(f"data/sources.json: venue_id inconnus: {', '.join(unknown_sources)}")
        unknown_bars = sorted({bar["id_inventaire"] for bar in bars if bar["id_inventaire"]} - venue_ids)
        if unknown_bars:
            raise ValueError(f"data/bars.json: id_inventaire inconnus: {', '.join(unknown_bars)}")
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Registres valides: {len(sources)} sources, {len(venues)} lieux, {len(bars)} bars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
