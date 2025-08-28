from application.template_parameter.read.dto import TemplateParameterRequestDTO
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)


def template_parameter_filter_from_dto(
    dto: TemplateParameterRequestDTO,
) -> TemplateParameterFilter:
    return TemplateParameterFilter(
        template_object_id=TemplateObjectId(dto.template_object_id),
        limit=50,
        offset=0,
    )
