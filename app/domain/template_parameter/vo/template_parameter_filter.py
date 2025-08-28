from dataclasses import dataclass

from domain.shared.vo.template_object_id import TemplateObjectId


@dataclass(frozen=True, slots=True)
class TemplateParameterFilter:
    template_object_id: TemplateObjectId

    limit: int
    offset: int
