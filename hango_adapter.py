"""Compatibility imports for official Hango widgets."""

from samstag.collection.adapters.hango import (
    API,
    KINDS,
    MAX_PAGES,
    collect_hango,
    parse_events,
)

__all__ = ["API", "KINDS", "MAX_PAGES", "collect_hango", "parse_events"]
