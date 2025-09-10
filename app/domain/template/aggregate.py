from dataclasses import dataclass
from datetime import datetime

from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from models import Template


@dataclass(slots=True, kw_only=True)
class TemplateAggregate:
    id: TemplateId
    name: str
    owner: str
    object_type_id: ObjectTypeId
    creation_date: datetime
    modification_date: datetime
    valid: bool
    version: int

    @classmethod
    def from_db(cls, template: Template):
        return cls(
            id=TemplateId(template.id),
            name=template.name,
            owner=template.owner,
            object_type_id=ObjectTypeId(template.object_type_id),
            creation_date=template.creation_date,
            modification_date=template.modification_date,
            valid=template.valid,
            version=template.version,
        )

    def update_name(self, new_name: str):
        if new_name != self.name:
            self.name = new_name

    def update_owner(self, new_owner: str):
        if new_owner != self.owner:
            self.owner = new_owner

    def update_object_type_id(self, new_object_type_id: int):
        if new_object_type_id != self.object_type_id:
            self.object_type_id = ObjectTypeId(new_object_type_id)

    def update_valid(self):
        if not self.valid:
            self.valid = True

    def update_version(self):
        self.version += 1
