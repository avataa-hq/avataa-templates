from dataclasses import dataclass

from domain.template_parameter.aggregate import TemplateParameterAggregate


# From router
@dataclass(frozen=True, slots=True)
class TemplateParameterDataUpdateRequestDTO:
    parameter_type_id: int
    required: bool

    value: str | None = None
    constraint: str | None = None


@dataclass(frozen=True, slots=True)
class TemplateParameterUpdateRequestDTO:
    template_parameter_id: int
    data: TemplateParameterDataUpdateRequestDTO


# From aggregate to router
@dataclass(frozen=True, slots=True)
class TemplateParameterUpdateDTO:
    id: int
    parameter_type_id: int
    value: str
    required: bool
    val_type: str
    valid: bool
    constraint: str | None = None

    @classmethod
    def from_aggregate(
        cls, aggregate: TemplateParameterAggregate
    ) -> "TemplateParameterUpdateDTO":
        return cls(
            id=aggregate.id,
            parameter_type_id=aggregate.parameter_type_id.to_raw(),
            value=aggregate.value,
            constraint=aggregate.constraint,
            required=aggregate.required,
            val_type=aggregate.val_type,
            valid=aggregate.valid,
        )
