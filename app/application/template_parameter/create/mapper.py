from application.paramater_validation.dto import (
    TemplateParameterValidationDTO,
    TemplateParameterValidationRequestDTO,
)
from application.template_parameter.create.dto import (
    TemplateParameterDataCreateRequestDTO,
)
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.template_parameter.vo.template_parameter_create import (
    TemplateParameterCreate,
)


def template_parameter_create_from_dto(
    dto: TemplateParameterDataCreateRequestDTO,
    template_object_id: int,
    val_type: str,
) -> TemplateParameterCreate:
    return TemplateParameterCreate(
        parameter_type_id=ParameterTypeId(dto.parameter_type_id),
        required=dto.required,
        value=dto.value,
        constraint=dto.constraint,
        template_object_id=TemplateObjectId(template_object_id),
        val_type=val_type,
    )


def template_parameter_to_validator(
    obj_type_id: int,
    data: list[TemplateParameterDataCreateRequestDTO],
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
