from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from application.template.read.dto import (
    TemplateRequestDTO,
    TemplateResponseDataDTO,
)
from application.template_object.read.dto import (
    TemplateObjectRequestDTO,
    TemplateObjectSearchDTO,
)
from application.template_parameter.create.dto import (
    TemplateParameterCreatedDTO,
    TemplateParameterDataCreateRequestDTO,
)
from application.template_parameter.read.dto import (
    TemplateParameterRequestDTO,
    TemplateParameterSearchDTO,
)


class TemplateParameterSearchRequest(BaseModel):
    template_object_id: int = Field(default=1, ge=1)

    def to_interactor_dto(self) -> TemplateParameterRequestDTO:
        return TemplateParameterRequestDTO(
            template_object_id=self.template_object_id,
        )


class TemplateParameterData(BaseModel):
    parameter_type_id: int = Field(default=1, ge=1)
    value: str | None = Field(default=None)
    constraint: str | None = Field(default=None)
    required: bool = Field(default=False)

    def to_create_request_dto(self) -> TemplateParameterDataCreateRequestDTO:
        return TemplateParameterDataCreateRequestDTO(
            parameter_type_id=self.parameter_type_id,
            value=self.value,
            constraint=self.constraint,
            required=self.required,
        )


class TemplateParameterCreateResponse(BaseModel):
    id: int
    parameter_type_id: int
    value: str
    constraint: str | None = Field(default=None)
    val_type: str
    required: bool
    valid: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_application_dto(
        cls, dto: TemplateParameterCreatedDTO
    ) -> "TemplateParameterCreateResponse":
        return cls.model_validate(dto, by_alias=True)


class TemplateParameterSearchResponse(BaseModel):
    id: int
    parameter_type_id: int
    value: str
    constraint: str | None = Field(default=None)
    val_type: str
    required: bool
    valid: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_application_dto(
        cls, dto: TemplateParameterSearchDTO
    ) -> "TemplateParameterSearchResponse":
        return cls.model_validate(dto, by_alias=True)


class TemplateObjectSearchRequest(BaseModel):
    template_object_id: int = Field(default=1, ge=1)
    parent_id: int | None = Field(
        default=None, ge=1, description="Parent object ID (optional)"
    )
    depth: int = Field(
        default=1,
        ge=1,
        description="Depth of children to retrieve (1 by default)",
    )
    include_parameters: bool = Field(
        default=False,
        description="Include parameters in the response (default: False)",
    )

    def to_interactor_dto(self) -> TemplateObjectRequestDTO:
        return TemplateObjectRequestDTO(
            template_object_id=self.template_object_id,
            parent_id=self.parent_id,
            depth=self.depth,
            include_parameters=self.include_parameters,
        )


class TemplateObjectSearchResponse(BaseModel):
    id: int
    object_type_id: int
    required: bool
    parameters: list[TemplateParameterSearchResponse]
    children: list
    valid: bool

    @classmethod
    def from_application_dto(
        cls, dto: TemplateObjectSearchDTO
    ) -> "TemplateObjectSearchResponse":
        return cls(
            id=dto.id,
            object_type_id=dto.object_type_id,
            required=dto.required,
            children=dto.children,
            valid=dto.valid,
            parameters=[
                TemplateParameterSearchResponse.from_application_dto(param)
                for param in dto.parameters
            ],
        )


class TemplateRequest(BaseModel):
    name: str | None = Field(default=None)
    owner: str | None = Field(default=None)
    object_type_id: int | None = Field(default=None, ge=1)

    limit: int = Field(default=50, ge=1)
    offset: int = Field(default=0, ge=0)

    def to_interactor_dto(self) -> TemplateRequestDTO:
        return TemplateRequestDTO(
            name=self.name,
            owner=self.owner,
            object_type_id=self.object_type_id,
            limit=self.limit,
            offset=self.offset,
        )


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
