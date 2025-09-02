from typing import Protocol

from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from domain.template_parameter.vo.template_parameter_exists import (
    TemplateParameterExists,
)
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)


class TemplateParameterReader(Protocol):
    async def exists(self, db_filter: TemplateParameterExists) -> bool: ...

    async def get_by_template_object_id(
        self, db_filter: TemplateParameterFilter
    ) -> list[TemplateParameterAggregate]: ...

    async def get_by_id(
        self, template_parameter_id: int
    ) -> TemplateParameterAggregate: ...

    async def get_by_ids(
        self, template_parameter_ids: list[int]
    ) -> list[TemplateParameterAggregate]: ...

    async def get_by_filters(
        self, db_filter: TemplateParameterExists
    ) -> list[TemplateParameterAggregate]: ...

    async def get_by_template_object_ids(
        self, template_object_ids: list[int]
    ) -> list[TemplateParameterAggregate]: ...
