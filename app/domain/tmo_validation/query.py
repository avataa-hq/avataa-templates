from typing import Protocol

from domain.tmo_validation.aggregate import InventoryTMOAggregate


class TMOReader(Protocol):
    async def get_all_tmo_data(self) -> list[InventoryTMOAggregate]: ...
