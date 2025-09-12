from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from pydantic import ValidationError

from application.template_object.delete.dto import (
    TemplateObjectDeleteRequestDTO,
)
from application.template_object.delete.exceptions import (
    TemplateObjectDeleterApplicationException,
)
from application.template_object.delete.interactors import (
    TemplateObjectDeleterInteractor,
)
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_object.read.interactors import (
    TemplateObjectByIdInteractor,
    TemplateObjectReaderInteractor,
)
from application.template_object.update.exceptions import (
    TemplateObjectUpdaterApplicationException,
)
from application.template_object.update.interactors import (
    TemplateObjectUpdaterInteractor,
)
from presentation.api.v1.endpoints.dto import (
    TemplateObjectSearchRequest,
    TemplateObjectSearchResponse,
    TemplateObjectSearchWithChildrenResponse,
    TemplateObjectSingleSearchRequest,
    TemplateObjectUpdateDataInput,
    TemplateObjectUpdateResponse,
)
from presentation.security.security_data_models import UserData
from presentation.security.security_factory import security

router = APIRouter(tags=["template-object"])


@router.get(
    "/object",
    status_code=status.HTTP_200_OK,
    response_model=TemplateObjectSearchResponse,
)
@inject
async def get_template_object(
    request: Annotated[TemplateObjectSingleSearchRequest, Query()],
    interactor: FromDishka[TemplateObjectByIdInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> TemplateObjectSearchResponse:
    try:
        result = await interactor(request=request.to_interactor_dto())
        return TemplateObjectSearchResponse.from_application_dto(result)

    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateObjectReaderApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.get(
    "/objects",
    status_code=status.HTTP_200_OK,
    response_model=list[TemplateObjectSearchWithChildrenResponse],
)
@inject
async def get_template_objects(
    request: Annotated[TemplateObjectSearchRequest, Query()],
    interactor: FromDishka[TemplateObjectReaderInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> list[TemplateObjectSearchWithChildrenResponse]:
    try:
        result = await interactor(request=request.to_interactor_dto())
        return [
            TemplateObjectSearchWithChildrenResponse.from_application_dto(res)
            for res in result
        ]
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateObjectReaderApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.put(
    "/objects/{object_id}",
    status_code=status.HTTP_200_OK,
    response_model=TemplateObjectUpdateResponse,
)
@inject
async def update_template_object(
    object_id: int,
    object_data: Annotated[
        TemplateObjectUpdateDataInput,
        Body(
            examples=[
                {
                    "required": True,
                    "parent_object_id": 1,
                }
            ]
        ),
    ],
    interactor: FromDishka[TemplateObjectUpdaterInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> TemplateObjectUpdateResponse:
    try:
        result = await interactor(
            request=object_data.to_interactor_dto(object_id=object_id)
        )
        output = TemplateObjectUpdateResponse.from_application_dto(result)
        return output
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateObjectUpdaterApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.delete(
    "/objects/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def delete_template_object(
    object_id: int,
    interactor: FromDishka[TemplateObjectDeleterInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> Response:
    try:
        request = TemplateObjectDeleteRequestDTO(template_object_id=object_id)
        await interactor(request=request)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateObjectDeleterApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
