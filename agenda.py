"""Compatibility entry point for samstag.domain.agenda."""
import sys

from samstag.domain import agenda as domain_agenda


# Keep legacy imports and clock patches on the same module state.
sys.modules[__name__] = domain_agenda
