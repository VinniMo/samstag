"""Researched places are distinct from active collection channels."""
import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[2] / "data"

BARS = json.loads((_DATA / "bars.json").read_text())
VENUES = json.loads((_DATA / "venues.json").read_text())
SOURCES = json.loads((_DATA / "sources.json").read_text())
PILOT_IDS = frozenset(f"B{i:03}" for i in range(1, 8))


def pilot_sources():
    # Inclusion authorizes a diagnostic fetch, not automatic publication.
    return [bar for bar in BARS if bar["id"] in PILOT_IDS]


def source_for(url):
    return next((source for source in SOURCES if source["canal"] == url), None)


def active_sources():
    return [source for source in SOURCES if source["enabled"]]
