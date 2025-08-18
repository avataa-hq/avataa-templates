from pydantic import BaseModel, Field


class TemplateParameterInput(BaseModel):
    parameter_type_id: int = Field(gt=0)
    value: str | None = None
    constraint: str | None = None
    required: bool = False


class TemplateObjectInput(BaseModel):
    object_type_id: int = Field(gt=0)
    required: bool = True
    parameters: list[TemplateParameterInput] | None = Field(
        default_factory=list
    )
    children: list["TemplateObjectInput"] | None = Field(default_factory=list)


class TemplateInput(BaseModel):
    name: str
    owner: str
    object_type_id: int = Field(gt=0)
    template_objects: list[TemplateObjectInput] | None = Field(
        default_factory=list
    )


class TemplateParameterOutput(BaseModel):
    id: int = Field(gt=0)
    parameter_type_id: int = Field(gt=0)
    value: str | None = None
    constraint: str | None = None
    required: bool = False
    val_type: str
    valid: bool | None = True


class TemplateObjectOutput(BaseModel):
    id: int = Field(gt=0)
    object_type_id: int = Field(gt=0)
    required: bool = True
    parameters: list[TemplateParameterOutput] | None = Field(
        default_factory=list
    )
    children: list["TemplateObjectOutput"] | None = Field(default_factory=list)
    valid: bool | None = True


class TemplateOutput(BaseModel):
    id: int = Field(gt=0)
    name: str
    owner: str
    object_type_id: int = Field(gt=0)
    template_objects: list[TemplateObjectOutput] | None = Field(
        default_factory=list
    )
    valid: bool | None = True


class TemplateObjectUpdateInput(BaseModel):
    required: bool
    parent_object_id: int | None = Field(default=None, gt=0)


class TemplateObjectUpdateOutput(BaseModel):
    id: int = Field(gt=0)
    object_type_id: int = Field(gt=0)
    parent_object_id: int | None = Field(default=None, gt=0)
    required: bool
    valid: bool | None = True


class SimpleTemplateOutput(BaseModel):
    id: int = Field(gt=0)
    name: str
    owner: str
    object_type_id: int = Field(gt=0)
    valid: bool | None = True


class TemplateUpdateInput(BaseModel):
    name: str
    owner: str
    object_type_id: int = Field(gt=0)


class TemplateUpdateOutput(BaseModel):
    id: int = Field(gt=0)
    name: str
    owner: str
    object_type_id: int = Field(gt=0)
    valid: bool | None = True
