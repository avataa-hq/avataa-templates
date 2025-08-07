from datetime import datetime
from dataclasses import dataclass

from application.template.reader.dto import (
    TemplateGatewayResponseDTO,
    TemplateResponseDataDTO,
)
from models import Template


@dataclass
class TemplateAggregate(object):
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

    @classmethod
    def from_dto(cls, dto: TemplateGatewayResponseDTO):
        return cls(
            id=dto.id,
            name=dto.name,
            owner=dto.owner,
            object_type_id=dto.object_type_id,
            creation_date=dto.creation_date,
            modification_date=dto.modification_date,
            valid=dto.valid,
            version=dto.version,
        )

    def to_response_dto(self) -> TemplateResponseDataDTO:
        return TemplateResponseDataDTO(
            id=self.id,
            name=self.name,
            owner=self.owner,
            object_type_id=self.object_type_id,
            creation_date=self.creation_date,
            modification_date=self.modification_date,
            valid=self.valid,
            version=self.version,
        )
