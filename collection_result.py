"""Compatibility entry point for samstag.collection.result."""
import sys

from samstag.collection import result


# Keep old and new imports on the same module state.
sys.modules[__name__] = result
