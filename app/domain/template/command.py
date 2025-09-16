from typing import Protocol

from domain.template.aggregate import TemplateAggregate


class TemplateCreator(Protocol):
    async def create_template(self, create_dto): ...


class TemplateUpdater(Protocol):
    async def update_template(self, template: TemplateAggregate): ...


class TemplateDeleter(Protocol):
    async def delete_template(self, db_filter): ...
