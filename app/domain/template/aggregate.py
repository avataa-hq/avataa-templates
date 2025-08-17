from dataclasses import dataclass
from datetime import datetime

from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from models import Template


@dataclass(frozen=True, slots=True)
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
