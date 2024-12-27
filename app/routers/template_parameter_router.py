from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas.template_schemas import (
    TemplateParameterInput,
    TemplateParameterOutput,
)
from services.template_parameter_services import TemplateParameterService
from exceptions import (
    TemplateObjectNotFound,
    TemplateParameterNotFound,
    TemplateObjectNotFound,
    TPRMNotFoundInInventory,
    RequiredMismatchException,
    InvalidParameterValue,
    ValueConstraintException,
    IncorrectConstraintException,
)


router = APIRouter(tags=["template-parameter"])


@router.get("/parameters")
async def get_template_object_parameters(
    template_object_id: int,
    db: AsyncSession = Depends(get_session),
) -> List[TemplateParameterOutput]:
    service = TemplateParameterService(db)

    try:
        return await service.get_all_by_template_object(template_object_id)
    except TemplateObjectNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template object not found"
        )


@router.put("/parameters/{parameter_id}")
async def update_template_parameter(
    parameter_id: int,
    parameter_data: TemplateParameterInput,
    db: AsyncSession = Depends(get_session),
) -> TemplateParameterOutput:
    service = TemplateParameterService(db)

    try:
        parameter = await service.update_template_parameter(
            parameter_data=parameter_data,
            parameter_id=parameter_id
        )
    except TemplateParameterNotFound:
        raise HTTPException(status_code=404, detail="Template parameter not found")
    except TPRMNotFoundInInventory as e:
        raise HTTPException(
            status_code=404,
            detail=(
                f"TPRM with id {e.parameter_type_id} not "
                f"found for TMO {e.object_type_id} in Inventory."
            )
        )
    except RequiredMismatchException as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except InvalidParameterValue as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except ValueConstraintException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except IncorrectConstraintException as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    await service.commit_changes()
    return parameter


@router.delete("/parameters/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template_parameter(
    parameter_id: int,
    db: AsyncSession = Depends(get_session),
):
    service = TemplateParameterService(db)

    try:
        await service.delete_template_parameter(parameter_id)
    except TemplateParameterNotFound:
        raise HTTPException(status_code=404, detail="Template parameter not found")

    await service.commit_changes()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
