from dataclasses import dataclass

from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateObjectCreate:
    template_id: TemplateId
    object_type_id: ObjectTypeId
    required: bool
    valid: bool

    parent_id: TemplateId | None = None
