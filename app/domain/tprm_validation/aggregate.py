from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryTprmAggregate:
    id: int
    multiple: bool
    name: str
    required: bool
    val_type: str

    constraint: str | None = None

    # Not implemented
    # returnable: bool
    # created_by: str
    # creation_date: datetime
    # modification_date: datetime
    # tmo_id: int
    # version: int
    #
    # modified_by: str | None = None
    # prm_link_filter: str | None = None
    # description: str | None = None
    # group: str | None = None
    # field_value: str | None = None
    # backward_ling: str | None = None
