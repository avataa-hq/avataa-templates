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
    async def update_template_parameters(
        self, template_parameter: TemplateParameterAggregate
    ) -> TemplateParameterAggregate: ...
