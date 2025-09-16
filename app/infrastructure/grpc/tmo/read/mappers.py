from typing import Any

from domain.tmo_validation.aggregate import InventoryTMOAggregate


def grpc_to_domain(data: dict[str, Any]) -> InventoryTMOAggregate:
    p_id_val = data.get("p_id")
    p_id: int | None = None if p_id_val is None else int(p_id_val)
    return InventoryTMOAggregate(
        id=int(data.get("id", 0)),
        parent_id=p_id,
    )
