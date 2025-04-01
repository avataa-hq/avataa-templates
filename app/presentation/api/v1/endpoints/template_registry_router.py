from typing import Annotated, Optional, List
from fastapi import (
    Body,
    Depends,
    APIRouter,
    HTTPException,
)

from application.common.uow import UoW
from presentation.api.depends_stub import Stub
from schemas.template_schemas import (
    TemplateInput,
    TemplateOutput,
    TemplateParameterInput,
    TemplateParameterOutput,
    TemplateObjectInput,
    TemplateObjectOutput,
)
from services.template_registry_services import (
    TemplateRegistryService,
)
from exceptions import (
    TemplateObjectNotFound,
    TemplateNotFound,
    TMOIdNotFoundInInventory,
    TPRMNotFoundInInventory,
    InvalidHierarchy,
    RequiredMismatchException,
    InvalidParameterValue,
    ValueConstraintException,
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


@router.post("/add-parameters/{template_object_id}/")
async def add_parameters(
    template_object_id: int,
    parameters_data: Annotated[
        List[TemplateParameterInput],
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
    db: Annotated[UoW, Depends(Stub(UoW))],
) -> List[TemplateParameterOutput]:
    service = TemplateRegistryService(db)

    try:
        service.get_template_object_or_raise(template_object_id)
    except TemplateObjectNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template object not found",
        )

    try:
        parameters = await service.create_template_parameters(
            parameters_data, template_object_id
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
    return parameters
