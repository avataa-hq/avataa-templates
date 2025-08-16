from dataclasses import dataclass

from application.template_parameter.read.dto import (
    TemplateParameterSearchDTO,
)
from domain.template_object.template_object import TemplateObjectAggregate
from domain.template_parameter.template_parameter import (
    TemplateParameterAggregate,
)


# From router
@dataclass(frozen=True, slots=True)
class TemplateObjectRequestDTO:
    template_object_id: int
    depth: int
    include_parameters: bool

    parent_id: int | None = None


# From aggregate to router
@dataclass(frozen=True, slots=True)
class TemplateObjectSearchDTO:
    id: int
    object_type_id: int
    required: bool
    parameters: list
    children: list  # Not implemented
    parameters: list[TemplateParameterSearchDTO]
    valid: bool

    @classmethod
    def from_aggregate(
        cls,
        aggregate: TemplateObjectAggregate,
        parameters: list[TemplateParameterAggregate],
    ) -> "TemplateObjectSearchDTO":
        return cls(
            id=aggregate.id,
            object_type_id=aggregate.object_type_id,
            required=aggregate.required,
            children=[],
            valid=aggregate.valid,
            parameters=[
                TemplateParameterSearchDTO.from_aggregate(param)
                for param in parameters
            ],
        )
