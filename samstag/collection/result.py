from dataclasses import dataclass


@dataclass
class CollectionResult:
    events: list[dict]
    method: str
    complete_snapshot: bool = False
    partial: bool = False
    pages_expected: int | None = None
    pages_read: int | None = None
    access_status: str = "ok"
    parse_status: str = "ok"
    completeness_status: str | None = None

    def __post_init__(self):
        if self.completeness_status is None:
            self.completeness_status = (
                "complete" if self.complete_snapshot and not self.partial
                else "partial" if self.partial else "unknown"
            )

    def __iter__(self):
        # Preserve the existing (events, method) reader contract.
        yield self.events
        yield self.method

    @classmethod
    def normalize(cls, value):
        """Adapt legacy ``(events, method)`` readers at one boundary."""
        if isinstance(value, cls):
            return value
        events, method = value
        return cls(events, method)
