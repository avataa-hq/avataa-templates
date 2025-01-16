from dataclasses import dataclass

from models import TemplateParameter


@dataclass
class TemplateParameterDTO(object):
    id: int
    template_object_id: int
    parameter_type_id: int
    value: str
    constraint: str
    required: bool
    val_type: str
    valid: bool

    @classmethod
    def from_db(
        cls, template_parameter: TemplateParameter
    ):
        return cls(
            id=template_parameter.id,
            template_object_id=template_parameter.template_object_id,
            parameter_type_id=template_parameter.parameter_type_id,
            value=template_parameter.value,
            constraint=template_parameter.constraint,
            required=template_parameter.required,
            val_type=template_parameter.val_type,
            valid=template_parameter.valid,
        )
