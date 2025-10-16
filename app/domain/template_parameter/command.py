from typing import Protocol

from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.template_parameter_create import (
    TemplateParameterCreate,
)


class TemplateParameterCreator(Protocol):
    async def create_template_parameters(
        self, create_dtos: list[TemplateParameterCreate]
    ) -> list[TemplateParameterAggregate]: ...


class TemplateParameterUpdater(Protocol):
    async def update_template_parameter(
        self, template_parameter: TemplateParameterAggregate
    ) -> TemplateParameterAggregate: ...

    async def bulk_update_template_parameter(
        self, template_parameters: list[TemplateParameterAggregate]
    ) -> list[TemplateParameterAggregate]: ...


class TemplateParameterDeleter(Protocol):
    async def delete_template_parameter(
        self, template_parameter_id: int
    ) -> None: ...
