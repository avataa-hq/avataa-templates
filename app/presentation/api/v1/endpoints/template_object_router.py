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
from sqlalchemy.ext.asyncio import AsyncSession

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
from di import (
    get_async_session,
)
from exceptions import (
    TemplateObjectNotFound,
)
from presentation.api.v1.endpoints.dto import (
    TemplateObjectSearchRequest,
    TemplateObjectSearchResponse,
    TemplateObjectSearchWithChildrenResponse,
    TemplateObjectSingleSearchRequest,
    TemplateObjectUpdateDataInput,
    TemplateObjectUpdateInp,
    TemplateObjectUpdateResponse,
)
from presentation.security.security_data_models import UserData
from presentation.security.security_factory import security
from services.template_object_services import (
    TemplateObjectService,
)

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
        updated_object = await interactor(
            request=TemplateObjectUpdateInp(
                object_id=object_id,
                object_data=object_data,
            ).to_interactor_dto()
        )
        output = TemplateObjectUpdateResponse.from_application_dto(
            updated_object
        )
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
async def delete_template_object(
    object_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[UserData, Depends(security)],
) -> Response:
    service = TemplateObjectService(db)

    try:
        await service.delete_template_object(object_id)
    except TemplateObjectNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template object not found",
        )

    await service.commit_changes()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
