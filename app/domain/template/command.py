from typing import Protocol


class TemplateCreator(Protocol):
    async def create_template(self, create_dto): ...


class TemplateUpdater(Protocol):
    async def update_template(self, db_filter): ...


class TemplateDeleter(Protocol):
    async def delete_template(self, db_filter): ...
