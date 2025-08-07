from abc import abstractmethod
from typing import Protocol

from application.template.reader.dto import (
    TemplateGatewayRequestDTO,
    TemplateGatewayResponseDTO,
)


class TemplateReader(Protocol):
    @abstractmethod
    async def get_all_templates(self): ...

    @abstractmethod
    async def get_template_by_filter(
        self, db_filter: TemplateGatewayRequestDTO
    ) -> list[TemplateGatewayResponseDTO]: ...


class TemplateCreator(Protocol):
    @abstractmethod
    async def create_template(self, create_dto): ...


class TemplateUpdater(Protocol):
    @abstractmethod
    async def update_template(self, db_filter): ...


class TemplateDeleter(Protocol):
    @abstractmethod
    async def delete_template(self, db_filter): ...
