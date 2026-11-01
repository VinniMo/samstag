from dataclasses import dataclass


@dataclass
class CollectionResult:
    events: list[dict]
    method: str
    complete_snapshot: bool = False
    partial: bool = False

    def __iter__(self):
        # Preserve the existing (events, method) reader contract.
        yield self.events
        yield self.method
