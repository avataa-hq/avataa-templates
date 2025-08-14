from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.params import Query
from presentation.api.depends_stub import Stub
from presentation.api.v1.endpoints.consts import USER_REQUEST
from presentation.api.v1.endpoints.dto import (
    TemplateParameterSearchRequest,
    TemplateParameterSearchResponse,
)
from pydantic import ValidationError

from application.common.uow import UoW
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from exceptions import (
    IncorrectConstraintException,
    InvalidParameterValue,
    RequiredMismatchException,
    TemplateParameterNotFound,
    TPRMNotFoundInInventory,
    ValueConstraintException,
)
from schemas.template_schemas import (
    TemplateParameterInput,
    TemplateParameterOutput,
)
from services.template_parameter_services import (
    TemplateParameterService,
)

router = APIRouter(tags=["template-parameter"])


@router.get(
    "/parameters",
    status_code=status.HTTP_200_OK,
    response_model=list[TemplateParameterSearchResponse],
)
async def get_template_object_parameters(
    request: Annotated[TemplateParameterSearchRequest, Query()],
    interactor: Annotated[
        TemplateParameterReaderInteractor,
        Depends(Stub(TemplateParameterReaderInteractor)),
    ],
) -> list[TemplateParameterSearchResponse]:
    try:
        result = await interactor(request=request.to_interactor_dto())
        return [
            TemplateParameterSearchResponse.from_application_dto(el)
            for el in result
        ]
    except ValidationError as ex:
        print(USER_REQUEST, request)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterReaderApplicationException as ex:
        print(USER_REQUEST, request)
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(USER_REQUEST, request)
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.put("/parameters/{parameter_id}")
async def update_template_parameter(
    parameter_id: int,
    parameter_data: TemplateParameterInput,
    db: Annotated[UoW, Depends(Stub(UoW))],
) -> TemplateParameterOutput:
    service = TemplateParameterService(db)

    try:
        parameter = await service.update_template_parameter(
            parameter_data=parameter_data,
            parameter_id=parameter_id,
        )
    except TemplateParameterNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template parameter not found",
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
    except IncorrectConstraintException as e:
        raise HTTPException(status_code=422, detail=str(e))
    await service.commit_changes()
    return parameter


@router.delete(
    "/parameters/{parameter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template_parameter(
    parameter_id: int,
    db: Annotated[UoW, Depends(Stub(UoW))],
) -> Response:
    service = TemplateParameterService(db)

    try:
        await service.delete_template_parameter(parameter_id)
    except TemplateParameterNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template parameter not found",
        )

    await service.commit_changes()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
