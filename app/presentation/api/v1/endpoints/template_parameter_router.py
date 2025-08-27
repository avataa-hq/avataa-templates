from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.params import Query
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from application.template_parameter.update.dto import (
    TemplateParameterUpdateRequestDTO,
)
from application.template_parameter.update.exceptions import (
    TemplateParameterUpdaterApplicationException,
)
from application.template_parameter.update.interactors import (
    BulkTemplateParameterUpdaterInteractor,
    TemplateParameterUpdaterInteractor,
)
from di import (
    bulk_update_template_parameter_interactor,
    get_async_session,
    read_template_parameter_interactor,
    update_template_parameter_interactor,
)
from exceptions import TemplateParameterNotFound
from presentation.api.v1.endpoints.dto import (
    TemplateParameterSearchRequest,
    TemplateParameterSearchResponse,
    TemplateParameterUpdateInput,
    TemplateParameterUpdateResponse,
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
        Depends(read_template_parameter_interactor),
    ],
) -> list[TemplateParameterSearchResponse]:
    try:
        result = await interactor(request=request.to_interactor_dto())
        return [
            TemplateParameterSearchResponse.from_application_dto(el)
            for el in result
        ]
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterReaderApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.put(
    "/parameters/{parameter_id}",
    status_code=status.HTTP_200_OK,
    response_model=TemplateParameterUpdateResponse,
)
async def update_template_parameter(
    parameter_id: int,
    parameter_data: TemplateParameterUpdateInput,
    interactor: Annotated[
        TemplateParameterUpdaterInteractor,
        Depends(update_template_parameter_interactor),
    ],
) -> TemplateParameterUpdateResponse:
    try:
        updated_parameter = await interactor(
            request=TemplateParameterUpdateRequestDTO(
                template_parameter_id=parameter_id,
                data=parameter_data.to_application_dto(),
            )
        )
        output = TemplateParameterUpdateResponse.from_application_dto(
            updated_parameter
        )
        return output
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterUpdaterApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.post(
    "/parameters/",
    status_code=status.HTTP_200_OK,
    response_model=TemplateParameterUpdateResponse,
)
async def update_template_parameters(
    request,
    interactor: Annotated[
        BulkTemplateParameterUpdaterInteractor,
        Depends(bulk_update_template_parameter_interactor),
    ],
) -> list[TemplateParameterUpdateResponse]:
    try:
        updated_parameter = await interactor(request=[])
        print(updated_parameter)
        return []
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterUpdaterApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.delete(
    "/parameters/{parameter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template_parameter(
    parameter_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
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
