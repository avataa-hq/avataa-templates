from application.template_object.read.dto import TemplateObjectRequestDTO
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)


def template_object_filter_from_dto(
    request: TemplateObjectRequestDTO,
) -> TemplateObjectFilter:
    return TemplateObjectFilter(
        template_id=request.template_object_id,
        depth=request.depth,
        parent_object_id=request.parent_id,
        include_parameters=request.include_parameters,
    )


def template_parameter_filter_from_dto(
    request: TemplateObjectRequestDTO,
) -> TemplateParameterFilter:
    return TemplateParameterFilter(
        template_object_id=request.template_object_id,
        limit=50,
        offset=0,
    )
