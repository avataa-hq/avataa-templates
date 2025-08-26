from application.paramater_validation.dto import (
    TemplateParameterValidationDTO,
    TemplateParameterValidationRequestDTO,
)
from application.template_parameter.update.dto import (
    TemplateParameterDataUpdateRequestDTO,
)


def template_parameter_to_validator(
    obj_type_id: int,
    data: list[TemplateParameterDataUpdateRequestDTO],
) -> TemplateParameterValidationRequestDTO:
    return TemplateParameterValidationRequestDTO(
        object_type_id=obj_type_id,
        parameter_to_validate=[
            TemplateParameterValidationDTO(
                parameter_type_id=el.parameter_type_id,
                value=el.value,
                required=el.required,
                constraint=el.constraint,
            )
            for el in data
        ],
    )
