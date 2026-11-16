"""Compatibility entry point for samstag.collection.registry."""
import sys

from samstag.collection import registry


# Keep old and new imports on the same module state.
sys.modules[__name__] = registry
