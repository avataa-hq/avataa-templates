from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryTMOAggregate:
    id: int
    name: str

    parent_id: int | None = None
