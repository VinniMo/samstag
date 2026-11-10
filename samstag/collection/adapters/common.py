"""Small shared building blocks for official programme adapters."""
import re
from datetime import date

from agenda import fold
from bar_adapters import base_event
from venue_adapters import MONTHS


def french_day(value):
    match = re.search(r"\b(\d{1,2})(?:er)?\s+(\w+)\s+(\d{4})\b", fold(value))
    if match and match[2] in MONTHS:
        try:
            return date(int(match[3]), MONTHS[match[2]], int(match[1]))
        except ValueError:
            pass
    return None


def event_at(title, page, evidence, venue, kind, category):
    event = base_event(title, page, evidence)
    event.update(location=venue, municipality="Lausanne", event_kind=kind,
                 category=category, adapter="official-programme-v3")
    return event
