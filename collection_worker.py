"""Compatibility entry point for samstag.collection.worker."""
import sys

from samstag.collection import worker


if __name__ == "__main__":
    raise SystemExit(worker.main())

# Keep old and new imports on the same module state.
sys.modules[__name__] = worker
