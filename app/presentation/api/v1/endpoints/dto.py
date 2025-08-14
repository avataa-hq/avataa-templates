from datetime import datetime

from pydantic import BaseModel, Field

from application.template.read.dto import (
    TemplateRequestDTO,
    TemplateResponseDataDTO,
)
from application.template_parameter.read.dto import (
    TemplateParameterRequestDTO,
    TemplateParameterSearchDTO,
)


class TemplateRequest(BaseModel):
    name: str | None = Field(default=None)
    owner: str | None = Field(default=None)
    object_type_id: int | None = Field(default=None, ge=1)

    limit: int = Field(default=50, ge=1)
    offset: int = Field(default=0, ge=0)

    def to_interactor_dto(self) -> TemplateRequestDTO:
        return TemplateRequestDTO(**self.model_dump(exclude_none=True))


class TemplateResponseDate(BaseModel):
    id: int
    name: str
    owner: str
    object_type_id: int
    creation_date: datetime
    modification_date: datetime
    valid: bool
    version: int

    @classmethod
    def from_dto(cls, dto: TemplateResponseDataDTO) -> "TemplateResponseDate":
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


class TemplateResponse(BaseModel):
    data: list[TemplateResponseDate]


class TemplateParameterSearchRequest(BaseModel):
    template_object_id: int = Field(default=1, ge=1)

    def to_interactor_dto(self) -> TemplateParameterRequestDTO:
        return TemplateParameterRequestDTO(**self.model_dump(exclude_none=True))


class TemplateParameterSearchResponse(BaseModel):
    id: int
    parameter_type_id: int = Field(
        serialization_alias="parameter_type_id",
        validation_alias="parameter_type_id",
    )
    value: str
    constraint: str | None = Field(default=None)
    val_type: str
    required: bool
    valid: bool

    class Config:
        from_attributes = True

    @classmethod
    def from_application_dto(
        cls, dto: TemplateParameterSearchDTO
    ) -> "TemplateParameterSearchResponse":
        return TemplateParameterSearchResponse.model_validate(
            dto, by_alias=True
        )
