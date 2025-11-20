from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.create.interactors import (
    TemplateObjectCreatorInteractor,
)
from application.template_parameter.create.dto import (
    TemplateParameterCreateRequestDTO,
)
from application.template_parameter.create.exceptions import (
    TemplateParameterCreatorApplicationException,
)
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
from di import get_async_session
from exceptions import (
    InvalidHierarchy,
    InvalidParameterValue,
    RequiredMismatchException,
    TemplateNotFound,
    TemplateObjectNotFound,
    TMOIdNotFoundInInventory,
    TPRMNotFoundInInventory,
    ValueConstraintException,
)
from presentation.api.v1.endpoints.dto import (
    TemplateObjectData,
    TemplateObjectRequest,
    TemplateParameterCreateResponse,
    TemplateParameterData,
)
from presentation.security.security_data_models import UserData
from presentation.security.security_factory import security
from schemas.template_schemas import (
    TemplateInput,
    TemplateObjectInput,
    TemplateObjectOutput,
    TemplateOutput,
)
from services.template_registry_services import TemplateRegistryService

router = APIRouter(tags=["template-registry"])


@router.post("/registry-template")
async def create_template(
    template_data: Annotated[
        TemplateInput,
        Body(
            examples=[
                {
                    "name": "Template Name",
                    "owner": "Admin",
                    "object_type_id": 1,
                    "template_objects": [
                        {
                            "object_type_id": 46181,
                            "required": True,
                            "parameters": [
                                {
                                    "parameter_type_id": 135296,
                                    "value": "Value 1",
                                    "constraint": "Value 1",
                                    "required": True,
                                },
                                {
                                    "parameter_type_id": 135297,
                                    "value": "[1, 2]",
                                    "required": False,
                                },
                                {
                                    "parameter_type_id": 135298,
                                    "value": "1234567",
                                    "constraint": None,
                                    "required": False,
                                },
                            ],
                            # "children": [
                            #     {
                            #         "object_type_id": 3,
                            #         "required": False,
                            #         "parameters": [],
                            #         "children": []
                            #     }
                            # ]
                        }
                    ],
                }
            ]
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[UserData, Depends(security)],
) -> TemplateOutput:
    service = TemplateRegistryService(db)
    try:
        template = await service.create_template(template_data)
    except TMOIdNotFoundInInventory as e:
        raise HTTPException(
            status_code=404,
            detail=f"TMO with id {e.object_type_id} not found in Inventory.",
        )
    except InvalidHierarchy as e:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid hierarchy: object_type_id {e.object_type_id} "
                f"expected parent {e.expected_parent_id}, got {e.actual_parent_id}."
            ),
        )
    except TPRMNotFoundInInventory as e:
        raise HTTPException(
            status_code=404,
            detail=(
                f"TPRM with id {e.parameter_type_id} not "
                f"found for TMO {e.object_type_id} in Inventory."
            ),
        )
    except RequiredMismatchException as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except InvalidParameterValue as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueConstraintException as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=422, detail=str(ex))
    await service.commit_changes()
    return template


@router.post("/add-objects/{template_id}")
async def add_objects(
    template_id: int,
    objects_data: Annotated[
        list[TemplateObjectInput],
        Body(
            examples=[
                [
                    {
                        "object_type_id": 46181,
                        "required": True,
                        "parameters": [
                            {
                                "parameter_type_id": 135296,
                                "value": "Value 1",
                                "constraint": "Value 1",
                                "required": True,
                            },
                        ],
                    },
                    {
                        "object_type_id": 3,
                        "required": False,
                        "parameters": [],
                        "children": [],
                    },
                ]
            ]
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[UserData, Depends(security)],
    parent_id: int | None = None,
) -> list[TemplateObjectOutput]:
    service = TemplateRegistryService(db)

    try:
        await service.get_template_or_raise(template_id)
    except TemplateNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    if parent_id:
        try:
            parent_object = await service.get_template_object_or_raise(
                parent_id
            )
        except TemplateObjectNotFound:
            raise HTTPException(
                status_code=404,
                detail="Parent template object not found",
            )

        if parent_object.template_id != template_id:
            raise HTTPException(
                status_code=400,
                detail="Parent template object isn't related to the template",
            )

    try:
        objects = await service.create_template_objects(
            objects_data,
            template_id,
            parent_id,
        )
    except TMOIdNotFoundInInventory as e:
        raise HTTPException(
            status_code=404,
            detail=f"TMO with id {e.object_type_id} not found in Inventory.",
        )
    except InvalidHierarchy as e:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid hierarchy: object_type_id {e.object_type_id} "
                f"expected parent {e.expected_parent_id}, got {e.actual_parent_id}."
            ),
        )
    except TPRMNotFoundInInventory as e:
        raise HTTPException(
            status_code=404,
            detail=(
                f"TPRM with id {e.parameter_type_id} not "
                f"found for TMO {e.object_type_id} in Inventory."
            ),
        )
    except RequiredMismatchException as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except InvalidParameterValue as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueConstraintException as e:
        raise HTTPException(status_code=422, detail=str(e))
    await service.commit_changes()
    return objects


@router.post("/add-objects_new/{template_id}")
@inject
async def add_objects_new(
    template_id: int,
    objects_data: Annotated[
        list[TemplateObjectData],
        Body(
            examples=[
                [
                    {
                        "object_type_id": 46181,
                        "required": True,
                        "parameters": [
                            {
                                "parameter_type_id": 135296,
                                "value": "Value 1",
                                "constraint": "Value 1",
                                "required": True,
                            },
                        ],
                    },
                    {
                        "object_type_id": 3,
                        "required": False,
                        "parameters": [],
                        "children": [],
                    },
                ]
            ]
        ),
    ],
    interactor: FromDishka[TemplateObjectCreatorInteractor],
    user_data: Annotated[UserData, Depends(security)],
    parent_id: int | None = None,
) -> list[TemplateObjectOutput]:
    try:
        req = TemplateObjectRequest(
            template_id=template_id,
            parent_id=parent_id,
            data=objects_data,
        )
        result = await interactor(request=req.to_interactor_dto())
        return result
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterCreatorApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.post(
    "/add-parameters/{template_object_id}",
    status_code=200,
    response_model=list[TemplateParameterCreateResponse],
)
@inject
async def add_parameters(
    template_object_id: int,
    parameters_data: Annotated[
        list[TemplateParameterData],
        Body(
            examples=[
                [
                    {
                        "parameter_type_id": 101,
                        "value": "New Parameter Value",
                        "constraint": "New Parameter Constraint",
                        "required": True,
                    },
                    {
                        "parameter_type_id": 102,
                        "value": "Another Parameter Value",
                        "constraint": None,
                        "required": False,
                    },
                ]
            ]
        ),
    ],
    interactor: FromDishka[TemplateParameterCreatorInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> list[TemplateParameterCreateResponse]:
    try:
        result = await interactor(
            request=TemplateParameterCreateRequestDTO(
                template_object_id=template_object_id,
                data=[
                    param.to_create_request_dto() for param in parameters_data
                ],
            )
        )
        return [
            TemplateParameterCreateResponse.from_application_dto(el)
            for el in result
        ]
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterCreatorApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
