from application.template_parameter.create.dto import (
    TemplateParameterDataCreateRequestDTO,
)
from domain.template_parameter.vo.template_parameter_create import (
    TemplateParameterCreate,
)


def template_parameter_create_from_dto(
    dto: TemplateParameterDataCreateRequestDTO,
    template_object_id: int,
    val_type: str,
) -> TemplateParameterCreate:
    return TemplateParameterCreate(
        parameter_type_id=dto.parameter_type_id,
        required=dto.required,
        value=dto.value,
        constraint=dto.constraint,
        template_object_id=template_object_id,
        val_type=val_type,
    )
