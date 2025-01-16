from __future__ import annotations
from pydantic import BaseModel, conint
from typing import List, Optional


class TemplateParameterInput(BaseModel):
    parameter_type_id: conint(gt=0)
    value: Optional[str] = None
    constraint: Optional[str] = None
    required: bool = False


class TemplateObjectInput(BaseModel):
    object_type_id: conint(gt=0)
    required: bool = True
    parameters: Optional[
        List[TemplateParameterInput]
    ] = []
    children: Optional[
        List["TemplateObjectInput"]
    ] = []


class TemplateInput(BaseModel):
    name: str
    owner: str
    object_type_id: conint(gt=0)
    template_objects: Optional[
        List[TemplateObjectInput]
    ] = []


class TemplateParameterOutput(BaseModel):
    id: conint(gt=0)
    parameter_type_id: conint(gt=0)
    value: Optional[str] = None
    constraint: Optional[str] = None
    required: bool = False
    val_type: str
    valid: Optional[bool] = True


class TemplateObjectOutput(BaseModel):
    id: conint(gt=0)
    object_type_id: conint(gt=0)
    required: bool = True
    parameters: Optional[
        List[TemplateParameterOutput]
    ] = []
    children: Optional[
        List["TemplateObjectOutput"]
    ] = []
    valid: Optional[bool] = True


class TemplateOutput(BaseModel):
    id: conint(gt=0)
    name: str
    owner: str
    object_type_id: conint(gt=0)
    template_objects: Optional[
        List[TemplateObjectOutput]
    ] = []
    valid: Optional[bool] = True


class TemplateObjectUpdateInput(BaseModel):
    required: bool
    parent_object_id: Optional[conint(gt=0)]


class TemplateObjectUpdateOutput(BaseModel):
    id: conint(gt=0)
    object_type_id: conint(gt=0)
    parent_object_id: Optional[conint(gt=0)]
    required: bool
    valid: Optional[bool] = True


class SimpleTemplateOutput(BaseModel):
    id: conint(gt=0)
    name: str
    owner: str
    object_type_id: conint(gt=0)
    valid: Optional[bool] = True


class TemplateUpdateInput(BaseModel):
    name: str
    owner: str
    object_type_id: conint(gt=0)


class TemplateUpdateOutput(BaseModel):
    id: conint(gt=0)
    name: str
    owner: str
    object_type_id: conint(gt=0)
    valid: Optional[bool] = True
