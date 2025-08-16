from dataclasses import dataclass

from domain.template_parameter.template_parameter import (
    TemplateParameterAggregate,
)


# From router
@dataclass(frozen=True, slots=True)
class TemplateParameterRequestDTO:
    template_object_id: int


# From aggregate to router
@dataclass(frozen=True, slots=True)
class TemplateParameterSearchDTO:
    id: int
    template_object_id: int
    parameter_type_id: int
    value: str
    constraint: str
    required: bool
    val_type: str
    valid: bool

    @classmethod
    def from_aggregate(
        cls, aggregate: TemplateParameterAggregate
    ) -> "TemplateParameterSearchDTO":
        return cls(
            id=aggregate.id,
            template_object_id=aggregate.template_object_id.to_raw(),
            parameter_type_id=aggregate.parameter_type_id.to_raw(),
            value=aggregate.value,
            constraint=aggregate.constraint,
            required=aggregate.required,
            val_type=aggregate.val_type,
            valid=aggregate.valid,
        )
