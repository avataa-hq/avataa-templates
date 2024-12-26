from datetime import datetime
from dataclasses import dataclass

from models import Template


@dataclass
class TemplateDTO(object):
    id: int
    name: str
    owner: str
    object_type_id: int
    creation_date: datetime
    modification_date: datetime
    valid: bool
    version: int

    @classmethod
    def from_db(cls, template: Template):
        return cls(
            id=template.id,
            name=template.name,
            owner=template.owner,
            object_type_id=template.object_type_id,
            creation_date=template.creation_date,
            modification_date=template.modification_date,
            valid=template.valid,
            version=template.version,
        )
