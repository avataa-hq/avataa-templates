from dataclasses import dataclass, field

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
    template_id: int
    depth: int
    include_parameters: bool

    parent_id: int | None = None


# From aggregate to router
@dataclass(frozen=True, slots=True)
class TemplateObjectSearchDTO:
    id: int
    template_id: int
    object_type_id: int
    required: bool
    parameters: list[TemplateParameterSearchDTO]
    valid: bool

    children: list["TemplateObjectSearchDTO"] = field(
        default_factory=list
    )  # Not implemented

    @classmethod
    def from_aggregate(
        cls,
        aggregate: TemplateObjectAggregate,
        parameters: list[TemplateParameterAggregate],
    ) -> "TemplateObjectSearchDTO":
        return cls(
            id=aggregate.id.to_raw(),
            template_id=aggregate.template_id.to_raw(),
            object_type_id=aggregate.object_type_id.to_raw(),
            required=aggregate.required,
            children=[],
            valid=aggregate.valid,
            parameters=[
                TemplateParameterSearchDTO.from_aggregate(param)
                for param in parameters
            ],
        )

    @classmethod
    def from_tree_aggregate(
        cls,
        tree: TemplateObjectAggregate,
        parameters: dict[int, list[TemplateParameterSearchDTO]],
    ) -> "TemplateObjectSearchDTO":
        object_id = tree.id.to_raw()
        object_parameters = parameters.get(object_id, []) if parameters else []
        children = [
            cls.from_tree_aggregate(child, parameters)
            for child in tree.children
        ]

        return cls(
            id=object_id,
            template_id=tree.template_id.to_raw(),
            object_type_id=tree.object_type_id.to_raw(),
            required=tree.required,
            children=children,
            valid=tree.valid,
            parameters=object_parameters,
        )
