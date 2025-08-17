from typing import Any

from domain.inventory_tprm.aggregate import InventoryTprmAggregate


def grpc_to_domain(data: dict[str, Any]) -> InventoryTprmAggregate:
    return InventoryTprmAggregate(
        val_type=data.get("val_type"),
        multiple=data.get("multiple"),
        required=data.get("required"),
        constraint=data.get("constraint"),
        id=data.get("id"),
    )
