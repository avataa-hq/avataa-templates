from typing import Protocol

from domain.tprm_validation.aggregate import InventoryTprmAggregate
from domain.tprm_validation.vo.validation_filter import (
    ParameterValidationFilter,
)


class TPRMReader(Protocol):
    async def get_all_tprms_by_tmo_id(
        self, grpc_filter: ParameterValidationFilter
    ) -> dict[int, InventoryTprmAggregate]: ...
