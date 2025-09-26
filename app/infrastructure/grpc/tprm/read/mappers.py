from typing import Any

from domain.tprm_validation.aggregate import InventoryTprmAggregate


def grpc_to_domain(data: dict[str, Any]) -> InventoryTprmAggregate:
    return InventoryTprmAggregate(
        id=int(data.get("id", -1)),
        required=bool(data.get("required")),
        multiple=bool(data.get("multiple")),
        name=data.get("name", ""),
        val_type=str(data.get("val_type")),
        constraint=data.get("constraint"),
    )
