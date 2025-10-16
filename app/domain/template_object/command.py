from typing import Protocol

from domain.template_object.aggregate import TemplateObjectAggregate


class TemplateObjectUpdater(Protocol):
    async def update_template_object(
        self, template_object: TemplateObjectAggregate
    ) -> TemplateObjectAggregate: ...


class TemplateObjectDeleter(Protocol):
    async def delete_template_object(self, template_object_id: int) -> None: ...
