from dataclasses import dataclass
from datetime import datetime


# From router
@dataclass
class TemplateRequestDTO:
    limit: int
    offset: int

    name: str | None = None
    owner: str | None = None
    object_type_id: int | None = None


# To gateway
@dataclass
class TemplateGatewayRequestDTO:
    limit: int
    offset: int

    name: str | None = None
    owner: str | None = None
    object_type_id: str | None = None


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


# To router
@dataclass
class TemplateResponseDTO:
    data: list[TemplateResponseDataDTO]
