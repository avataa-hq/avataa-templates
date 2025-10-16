from dataclasses import dataclass

from domain.shared.vo.template_object_id import TemplateObjectId


@dataclass(frozen=True, slots=True)
class TemplateObjectByIdFilter:
    id: TemplateObjectId
