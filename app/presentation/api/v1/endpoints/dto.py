from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from application.template.read.dto import (
    TemplateRequestDTO,
    TemplateResponseDataDTO,
)
from application.template_object.read.dto import (
    TemplateObjectByIdRequestDTO,
    TemplateObjectRequestDTO,
    TemplateObjectSearchDTO,
    TemplateObjectWithChildrenSearchDTO,
)
from application.template_object.update.dto import (
    TemplateObjectDataUpdateRequestDTO,
    TemplateObjectUpdateDTO,
)
from application.template_parameter.create.dto import (
    TemplateParameterCreatedDTO,
    TemplateParameterDataCreateRequestDTO,
)
from application.template_parameter.read.dto import (
    TemplateParameterRequestDTO,
    TemplateParameterSearchDTO,
)
from application.template_parameter.update.dto import (
    TemplateParameterBulkUpdateRequestDTO,
    TemplateParameterUpdateDTO,
    TemplateParameterUpdateRequestDTO,
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


class TemplateObjectSingleSearchRequest(BaseModel):
    id: int = Field(default=1, ge=1)
    include_parameters: bool = Field(
        default=False,
        description="Include parameters in the response (default: False)",
    )

    def to_interactor_dto(self) -> TemplateObjectByIdRequestDTO:
        return TemplateObjectByIdRequestDTO(
            id=self.id,
            include_parameters=self.include_parameters,
        )


class TemplateObjectSearchRequest(BaseModel):
    template_id: int = Field(default=1, ge=1)
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
            template_id=self.template_id,
            parent_id=self.parent_id,
            depth=self.depth,
            include_parameters=self.include_parameters,
        )


class TemplateObjectSearchResponse(BaseModel):
    id: int
    template_id: int
    object_type_id: int
    required: bool
    parameters: list[TemplateParameterSearchResponse]
    valid: bool

    @classmethod
    def from_application_dto(
        cls, dto: TemplateObjectSearchDTO
    ) -> "TemplateObjectSearchResponse":
        return cls(
            id=dto.id,
            template_id=dto.template_id,
            object_type_id=dto.object_type_id,
            required=dto.required,
            valid=dto.valid,
            parameters=[
                TemplateParameterSearchResponse.from_application_dto(param)
                for param in dto.parameters
            ],
        )


class TemplateObjectSearchWithChildrenResponse(TemplateObjectSearchResponse):
    children: list

    @classmethod
    def from_application_dto(
        cls, dto: TemplateObjectWithChildrenSearchDTO
    ) -> "TemplateObjectSearchWithChildrenResponse":
        return cls(
            id=dto.id,
            template_id=dto.template_id,
            object_type_id=dto.object_type_id,
            required=dto.required,
            children=[
                cls.from_application_dto(child) for child in dto.children
            ],
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
    def from_application_dto(
        cls, dto: TemplateResponseDataDTO
    ) -> "TemplateResponseDate":
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


class TemplateParameterUpdateInput(BaseModel):
    parameter_type_id: int = Field(gt=0)
    required: bool

    value: str | None = None
    constraint: str | None = None

    def to_interactor_dto(
        self, parameter_id: int
    ) -> TemplateParameterUpdateRequestDTO:
        return TemplateParameterUpdateRequestDTO(
            id=parameter_id,
            parameter_type_id=self.parameter_type_id,
            required=self.required,
            value=self.value,
            constraint=self.constraint,
        )


class TemplateParameterUpdateResponse(BaseModel):
    id: int = Field(gt=0)
    parameter_type_id: int = Field(gt=0)
    value: str | None = None
    constraint: str | None = None
    required: bool = False
    val_type: str
    valid: bool | None = True

    @classmethod
    def from_application_dto(
        cls, dto: TemplateParameterUpdateDTO
    ) -> "TemplateParameterUpdateResponse":
        return cls(
            id=dto.id,
            parameter_type_id=dto.parameter_type_id,
            value=dto.value,
            constraint=dto.constraint,
            required=dto.required,
            val_type=dto.val_type,
            valid=dto.valid,
        )


class TemplateParameterBulkUpdateData(TemplateParameterUpdateInput):
    id: int = Field(ge=1)

    def to_interactor_dto(
        self, parameter_id: int | None = None
    ) -> TemplateParameterUpdateRequestDTO:
        return TemplateParameterUpdateRequestDTO(
            id=self.id,
            parameter_type_id=self.parameter_type_id,
            required=self.required,
            value=self.value,
            constraint=self.constraint,
        )


class TemplateParameterBulkUpdateRequest(BaseModel):
    template_object_id: int = Field(ge=1)
    parameters: list[TemplateParameterBulkUpdateData]

    def to_interactor_dto(self) -> TemplateParameterBulkUpdateRequestDTO:
        return TemplateParameterBulkUpdateRequestDTO(
            template_object_id=self.template_object_id,
            data=[el.to_interactor_dto() for el in self.parameters],
        )


class TemplateObjectUpdateDataInput(BaseModel):
    required: bool = False
    parent_object_id: int | None = Field(default=None, ge=1)


class TemplateObjectUpdateInp(BaseModel):
    object_id: int = Field(ge=1)
    object_data: TemplateObjectUpdateDataInput

    def to_interactor_dto(self) -> TemplateObjectDataUpdateRequestDTO:
        return TemplateObjectDataUpdateRequestDTO(
            template_object_id=self.object_id,
            required=self.object_data.required,
            parent_object_id=self.object_data.parent_object_id,
        )


class TemplateObjectUpdateResponse(BaseModel):
    id: int
    template_id: int
    object_type_id: int
    required: bool
    valid: bool
    parent_object_id: int | None = Field(default=None)

    @classmethod
    def from_application_dto(
        cls, dto: TemplateObjectUpdateDTO
    ) -> "TemplateObjectUpdateResponse":
        return cls(
            id=dto.id,
            template_id=dto.template_id,
            object_type_id=dto.object_type_id,
            required=dto.required,
            valid=dto.valid,
            parent_object_id=dto.parent_object_id,
        )
