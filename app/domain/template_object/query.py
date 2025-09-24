from typing import Protocol

from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.vo.template_object_by_id_filter import (
    TemplateObjectByIdFilter,
)
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)


class TemplateObjectReader(Protocol):
    async def get_by_id(
        self, template_object_id: TemplateObjectByIdFilter
    ) -> TemplateObjectAggregate: ...

    async def get_by_ids(
        self, template_object_ids: list[int]
    ) -> list[TemplateObjectAggregate]: ...

    async def get_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]: ...

    async def get_by_object_type_ids(
        self, object_type_ids: list[int]
    ) -> list[TemplateObjectAggregate]: ...

    async def get_tree_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]: ...

    async def get_reverse_tree_by_id(
        self, children_id: int
    ) -> list[TemplateObjectAggregate]: ...

    async def exists(self, db_filter: TemplateObjectFilter) -> bool: ...

    async def get_object_type_by_id(
        self, db_filter: TemplateObjectFilter
    ) -> int: ...

    async def get_validity_by_template_id(
        self, template_id: int
    ) -> list[bool]: ...

    async def get_by_template_ids(
        self, template_ids: list[int]
    ) -> list[TemplateObjectAggregate]: ...
