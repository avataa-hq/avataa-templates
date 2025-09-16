from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.params import Query
from pydantic import ValidationError

from application.template_parameter.delete.dto import (
    TemplateParameterDeleteRequestDTO,
)
from application.template_parameter.delete.exceptions import (
    TemplateParameterDeleterApplicationException,
)
from application.template_parameter.delete.interactors import (
    TemplateParameterDeleterInteractor,
)
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from application.template_parameter.update.exceptions import (
    TemplateParameterUpdaterApplicationException,
)
from application.template_parameter.update.interactors import (
    BulkTemplateParameterUpdaterInteractor,
    TemplateParameterUpdaterInteractor,
)
from presentation.api.v1.endpoints.dto import (
    TemplateParameterBulkUpdateRequest,
    TemplateParameterSearchRequest,
    TemplateParameterSearchResponse,
    TemplateParameterUpdateInput,
    TemplateParameterUpdateResponse,
)
from presentation.security.security_data_models import UserData
from presentation.security.security_factory import security

router = APIRouter(tags=["template-parameter"])


@router.get(
    "/parameters",
    status_code=status.HTTP_200_OK,
    response_model=list[TemplateParameterSearchResponse],
)
@inject
async def get_template_object_parameters(
    request: Annotated[TemplateParameterSearchRequest, Query()],
    interactor: FromDishka[TemplateParameterReaderInteractor],
    user_data: Annotated[UserData, Depends(security)],
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
@inject
async def update_template_parameter(
    parameter_id: int,
    parameter_data: TemplateParameterUpdateInput,
    interactor: FromDishka[TemplateParameterUpdaterInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> TemplateParameterUpdateResponse:
    try:
        updated_parameter = await interactor(
            request=parameter_data.to_interactor_dto(parameter_id),
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
    "/parameters",
    status_code=status.HTTP_200_OK,
    response_model=list[TemplateParameterUpdateResponse],
)
@inject
async def update_template_parameters(
    request: TemplateParameterBulkUpdateRequest,
    interactor: FromDishka[BulkTemplateParameterUpdaterInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> list[TemplateParameterUpdateResponse]:
    try:
        updated_parameter = await interactor(
            request=request.to_interactor_dto()
        )
        output = [
            TemplateParameterUpdateResponse.from_application_dto(param)
            for param in updated_parameter
        ]
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


@router.delete(
    "/parameters/{parameter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_template_parameter(
    parameter_id: int,
    interactor: FromDishka[TemplateParameterDeleterInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> Response:
    try:
        request = TemplateParameterDeleteRequestDTO(
            template_parameter_id=parameter_id
        )
        await interactor(request=request)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateParameterDeleterApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
