"""Researched places are distinct from active collection channels."""
import json
from pathlib import Path

BARS = json.loads((Path(__file__).parent / "data" / "bars.json").read_text())
VENUES = json.loads((Path(__file__).parent / "data" / "venues.json").read_text())
SOURCES = json.loads((Path(__file__).parent / "data" / "sources.json").read_text())
PILOT_IDS = frozenset(f"B{i:03}" for i in range(1, 8))


def pilot_sources():
    # Inclusion authorizes a diagnostic fetch, not automatic publication.
    return [bar for bar in BARS if bar["id"] in PILOT_IDS]


def source_for(url):
    return next((source for source in SOURCES if source["canal"] == url), None)


def active_sources():
    return [source for source in SOURCES if source["enabled"]]
