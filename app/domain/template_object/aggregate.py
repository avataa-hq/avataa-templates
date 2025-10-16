from dataclasses import dataclass, field

from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from models import TemplateObject


@dataclass(kw_only=True, slots=True)
class TemplateObjectAggregate(object):
    id: TemplateObjectId
    template_id: TemplateId
    object_type_id: ObjectTypeId
    required: bool
    valid: bool

    parent_object_id: int | None = None

    children: list["TemplateObjectAggregate"] = field(default_factory=list)

    @classmethod
    def from_db(cls, template_object: TemplateObject):
        return cls(
            id=TemplateObjectId(template_object.id),
            template_id=TemplateId(template_object.template_id),
            parent_object_id=template_object.parent_object_id,
            object_type_id=ObjectTypeId(template_object.object_type_id),
            required=template_object.required,
            valid=template_object.valid,
        )

    def update_parent_object_id(self, parent_object_id: int | None) -> None:
        self.parent_object_id = parent_object_id

    def update_required(self, required: bool) -> None:
        self.required = required

    def set_valid(self, valid: bool) -> None:
        self.valid = valid
