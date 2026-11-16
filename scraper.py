"""Compatibility entry point for samstag.collection.runner."""
import sys

from samstag.collection import runner


# Keep old and new imports on the same module state.
sys.modules[__name__] = runner
