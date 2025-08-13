from application.template.read.dto import TemplateRequestDTO
from domain.template.vo.template_filter import TemplateFilter


def template_filter_from_dto(dto: TemplateRequestDTO) -> TemplateFilter:
    return TemplateFilter(
        name=dto.name,
        owner=dto.owner,
        object_type_id=dto.object_type_id,
        limit=dto.limit,
        offset=dto.offset,
    )
