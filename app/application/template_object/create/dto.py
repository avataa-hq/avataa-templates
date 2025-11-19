from dataclasses import dataclass

from application.template_parameter.create.dto import (
    TemplateParameterDataCreateRequestDTO,
)


# From router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateObjectCreateRequestDTO:
    template_id: int
    parent_id: int | None = None
    object_type_id: int
    required: bool

    parameters: list[TemplateParameterDataCreateRequestDTO]
    children: list["TemplateObjectCreateRequestDTO"]
