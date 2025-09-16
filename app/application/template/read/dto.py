from dataclasses import dataclass
from datetime import datetime

from domain.template.aggregate import TemplateAggregate


# From router
@dataclass
class TemplateRequestDTO:
    limit: int
    offset: int

    name: str | None = None
    owner: str | None = None
    object_type_id: int | None = None


# From gateway
@dataclass
class TemplateGatewayResponseDTO:
    id: int
    name: str
    owner: str
    object_type_id: int
    creation_date: datetime
    modification_date: datetime
    valid: bool
    version: int


# From aggregate to router
@dataclass
class TemplateResponseDataDTO:
    id: int
    name: str
    owner: str
    object_type_id: int
    creation_date: datetime
    modification_date: datetime
    valid: bool
    version: int

    @classmethod
    def from_aggregate(
        cls, aggregate: TemplateAggregate
    ) -> "TemplateResponseDataDTO":
        return cls(
            id=aggregate.id.to_raw(),
            name=aggregate.name,
            owner=aggregate.owner,
            object_type_id=aggregate.object_type_id.to_raw(),
            creation_date=aggregate.creation_date,
            modification_date=aggregate.modification_date,
            valid=aggregate.valid,
            version=aggregate.version,
        )


# To router
@dataclass
class TemplateResponseDTO:
    data: list[TemplateResponseDataDTO]
