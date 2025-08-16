from typing import (
    Annotated,
)

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from presentation.api.depends_stub import Stub
from presentation.api.v1.endpoints.consts import USER_REQUEST_MESSAGE
from presentation.api.v1.endpoints.dto import (
    TemplateObjectSearchRequest,
    TemplateObjectSearchResponse,
)
from pydantic import ValidationError

from application.common.uow import UoW
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_object.read.interactors import (
    TemplateObjectReaderInteractor,
)
from exceptions import (
    InvalidHierarchy,
    TemplateObjectNotFound,
)
from schemas.template_schemas import (
    TemplateObjectUpdateInput,
    TemplateObjectUpdateOutput,
)
from services.template_object_services import (
    TemplateObjectService,
)

router = APIRouter(tags=["template-object"])


@router.get(
    "/objects",
    status_code=status.HTTP_200_OK,
    response_model=list[TemplateObjectSearchResponse],
)
async def get_template_objects(
    request: Annotated[TemplateObjectSearchRequest, Query()],
    interactor: Annotated[
        TemplateObjectReaderInteractor,
        Depends(Stub(TemplateObjectReaderInteractor)),
    ],
) -> list[TemplateObjectSearchResponse]:
    try:
        result = await interactor(request=request.to_interactor_dto())
        return [
            TemplateObjectSearchResponse.from_application_dto(el)
            for el in result
        ]
    except ValidationError as ex:
        print(USER_REQUEST_MESSAGE, request)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateObjectReaderApplicationException as ex:
        print(USER_REQUEST_MESSAGE, request)
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(USER_REQUEST_MESSAGE, request)
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.put("/objects/{parameter_id}")
async def update_template_object(
    object_id: int,
    object_data: Annotated[
        TemplateObjectUpdateInput,
        Body(
            example={
                "required": True,
                "parent_object_id": 1,
            }
        ),
    ],
    db: Annotated[UoW, Depends(Stub(UoW))],
) -> TemplateObjectUpdateOutput:
    service = TemplateObjectService(db)

    try:
        obj = await service.update_template_object(
            object_data=object_data,
            object_id=object_id,
        )
    except TemplateObjectNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidHierarchy as e:
        raise HTTPException(status_code=422, detail=str(e))
    await service.commit_changes()
    return obj


@router.delete(
    "/objects/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template_object(
    object_id: int,
    db: Annotated[UoW, Depends(Stub(UoW))],
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
