from application.template_object.read.dto import TemplateObjectRequestDTO
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)


def template_object_filter_from_dto(
    request: TemplateObjectRequestDTO,
) -> TemplateObjectFilter:
    return TemplateObjectFilter(
        template_id=request.template_object_id,
        parent_object_id=request.parent_id,
        depth=request.depth,
    )
