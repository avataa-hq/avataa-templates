from typing import Protocol

from domain.template_object.template_object import TemplateObjectAggregate
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)


class TemplateObjectReader(Protocol):
    async def get_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]: ...
