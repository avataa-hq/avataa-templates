from dataclasses import dataclass

from models import TemplateObject


@dataclass
class TemplateObjectAggregate(object):
    id: int
    template_id: int
    parent_object_id: int
    object_type_id: int
    required: bool
    valid: bool

    @classmethod
    def from_db(cls, template_object: TemplateObject):
        return cls(
            id=template_object.id,
            template_id=template_object.template_id,
            parent_object_id=template_object.parent_object_id,
            object_type_id=template_object.object_type_id,
            required=template_object.required,
            valid=template_object.valid,
        )
