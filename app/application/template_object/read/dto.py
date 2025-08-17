from dataclasses import dataclass

from application.template_parameter.read.dto import (
    TemplateParameterSearchDTO,
)
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_parameter.aggregate import (
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
            id=aggregate.id.to_raw(),
            object_type_id=aggregate.object_type_id.to_raw(),
            required=aggregate.required,
            children=[],
            valid=aggregate.valid,
            parameters=[
                TemplateParameterSearchDTO.from_aggregate(param)
                for param in parameters
            ],
        )
