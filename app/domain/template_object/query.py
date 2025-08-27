from typing import Protocol

from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)


class TemplateObjectReader(Protocol):
    async def get_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]: ...

    async def get_tree_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]: ...

    async def exists(self, db_filter: TemplateObjectFilter) -> bool: ...

    async def get_object_type_by_id(
        self, db_filter: TemplateObjectFilter
    ) -> int: ...
