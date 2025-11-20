from typing import Protocol

from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.vo.template_object_create import (
    TemplateObjectCreate,
)


class TemplateObjectCreator(Protocol):
    async def create_template_object(
        self, create_dtos: list[TemplateObjectCreate]
    ) -> list[TemplateObjectAggregate]: ...


class TemplateObjectUpdater(Protocol):
    async def update_template_object(
        self, template_object: TemplateObjectAggregate
    ) -> TemplateObjectAggregate: ...


class TemplateObjectDeleter(Protocol):
    async def delete_template_object(self, template_object_id: int) -> None: ...
