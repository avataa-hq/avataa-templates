from typing import Any

from domain.inventory_tprm.aggregate import InventoryTprmAggregate


def grpc_to_domain(data: dict[str, Any]) -> InventoryTprmAggregate:
    return InventoryTprmAggregate(
        val_type=str(data.get("val_type")),
        multiple=bool(data.get("multiple")),
        required=bool(data.get("required")),
        constraint=data.get("constraint"),
        id=int(data.get("id", -1)),
    )
