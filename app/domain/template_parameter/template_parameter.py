from dataclasses import dataclass

from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.template_parameter.vo.template_object_id import TemplateObjectId
from models import TemplateParameter


@dataclass(frozen=True, slots=True)
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
