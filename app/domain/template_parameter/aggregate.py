from dataclasses import dataclass

from domain.common.exceptions import (
    ConstraintViolationError,
    EmptyValueError,
    RequiredParameterError,
)
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from models import TemplateParameter


@dataclass(kw_only=True, slots=True)
class TemplateParameterAggregate:
    id: int
    template_object_id: TemplateObjectId
    parameter_type_id: ParameterTypeId
    value: str
    required: bool
    val_type: str
    valid: bool

    constraint: str | None = None

    @classmethod
    def from_db(cls, template_parameter: TemplateParameter):
        return cls(
            id=template_parameter.id,
            template_object_id=TemplateObjectId(
                template_parameter.template_object_id
            ),
            parameter_type_id=ParameterTypeId(
                template_parameter.parameter_type_id
            ),
            value=template_parameter.value,
            constraint=template_parameter.constraint,
            required=template_parameter.required,
            val_type=template_parameter.val_type,
            valid=template_parameter.valid,
        )

    def update_parameter_type(self, new_type_id: int) -> None:
        if self.parameter_type_id != new_type_id:
            self.constraint = None
        self.parameter_type_id = ParameterTypeId(new_type_id)

    def set_value(self, new_value: str) -> None:
        if not new_value.strip():
            raise EmptyValueError("Parameter value cannot be empty.")

        if self.constraint and not self._validate_constraint(new_value):
            raise ConstraintViolationError(
                f"Value {new_value} violates constraint {self.constraint}."
            )

        self.valid = True
        self.value = new_value

    def set_required_flag(self, required: bool) -> None:
        if required and not self.value:
            raise RequiredParameterError("Parameter value must not be empty.")
        self.required = required

    def set_constraint(self, constraint: str) -> None:
        self.constraint = constraint

    def _validate_constraint(self, new_value: str) -> bool:
        print(f"Should validate constraint {new_value}")
        return True
