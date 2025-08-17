from typing import Annotated, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from presentation.api.depends_stub import Stub
from presentation.api.v1.endpoints.consts import USER_REQUEST_MESSAGE
from presentation.api.v1.endpoints.dto import (
    TemplateParameterCreateResponse,
    TemplateParameterData,
)
from pydantic import ValidationError

from application.common.uow import UoW
from application.template_parameter.create.dto import (
    TemplateParameterCreateRequestDTO,
)
from application.template_parameter.create.exceptions import (
    TemplateParameterCreatorApplicationException,
)
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
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
from schemas.template_schemas import (
    TemplateInput,
    TemplateObjectInput,
    TemplateObjectOutput,
    TemplateOutput,
)
from services.template_registry_services import (
    TemplateRegistryService,
)

router = APIRouter(tags=["template-registry"])


@router.post("/registry-template")
async def create_template(
    template_data: Annotated[
        TemplateInput,
        Body(
            example={
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
        ),
    ],
    db: Annotated[UoW, Depends(Stub(UoW))],
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
    await service.commit_changes()
    return template


@router.post("/add-objects/{template_id}/")
async def add_objects(
    template_id: int,
    objects_data: Annotated[
        List[TemplateObjectInput],
        Body(
            example=[
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
        ),
    ],
    db: Annotated[UoW, Depends(Stub(UoW))],
    parent_id: Optional[int] = None,
) -> List[TemplateObjectOutput]:
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


@router.post(
    "/add-parameters/{template_object_id}/",
    status_code=200,
    response_model=list[TemplateParameterCreateResponse],
)
async def add_parameters(
    template_object_id: int,
    parameters_data: Annotated[
        list[TemplateParameterData],
        Body(
            example=[
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
        ),
    ],
    interactor: Annotated[
        TemplateParameterCreatorInteractor,
        Depends(Stub(TemplateParameterCreatorInteractor)),
    ],
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
        print(USER_REQUEST_MESSAGE, parameters_data)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterCreatorApplicationException as ex:
        print(USER_REQUEST_MESSAGE, parameters_data)
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(USER_REQUEST_MESSAGE, parameters_data)
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
