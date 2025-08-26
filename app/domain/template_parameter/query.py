from typing import Protocol

from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)


class TemplateParameterReader(Protocol):
    async def get_by_filter(
        self, db_filter: TemplateParameterFilter
    ) -> list[TemplateParameterAggregate]: ...

    async def get_by_id(
        self, template_parameter_id: int
    ) -> TemplateParameterAggregate: ...
