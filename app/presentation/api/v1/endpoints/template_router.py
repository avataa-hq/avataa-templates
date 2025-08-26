from typing import Annotated, List, Optional

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

from application.template.read.exceptions import TemplateApplicationException
from application.template.read.interactors import TemplateReaderInteractor
from di import get_async_session, read_template_interactor
from exceptions import (
    TemplateNotFound,
    TMOIdNotFoundInInventory,
)
from presentation.api.v1.endpoints.consts import USER_REQUEST_MESSAGE
from presentation.api.v1.endpoints.dto import (
    TemplateRequest,
    TemplateResponse,
    TemplateResponseDate,
)
from schemas.template_schemas import (
    SimpleTemplateOutput,
    TemplateUpdateInput,
    TemplateUpdateOutput,
)
from services.template_services import TemplateService

router = APIRouter(tags=["template"])


@router.get("/templates")
async def get_templates(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Number of templates to return",
    ),
    offset: Optional[int] = Query(
        None,
        ge=0,
        description="Number of templates to skip",
    ),
) -> List[SimpleTemplateOutput]:
    service = TemplateService(db)
    result = await service.get_templates(limit=limit, offset=offset)
    return result


@router.post(
    "/search", status_code=status.HTTP_200_OK, response_model=TemplateResponse
)
async def get_templates_by_filter(
    request: TemplateRequest,
    interactor: Annotated[
        TemplateReaderInteractor, Depends(read_template_interactor)
    ],
) -> TemplateResponse:
    try:
        result = await interactor(request=request.to_interactor_dto())
        output_data: list[TemplateResponseDate] = list()
        for application_el in result.data:
            el = TemplateResponseDate.from_application_dto(application_el)
            output_data.append(el)
        return TemplateResponse(data=output_data)
    except ValidationError as ex:
        print(USER_REQUEST_MESSAGE, request)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateApplicationException as ex:
        print(USER_REQUEST_MESSAGE, request)
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(USER_REQUEST_MESSAGE, request)
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    template_data: Annotated[
        TemplateUpdateInput,
        Body(
            examples=[
                {
                    "name": "Template Name X",
                    "owner": "Updated Owner",
                    "object_type_id": 1,
                }
            ]
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> TemplateUpdateOutput:
    service = TemplateService(db)

    try:
        template = await service.update_template(
            template_id=template_id,
            template_data=template_data,
        )
    except TemplateNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TMOIdNotFoundInInventory as e:
        raise HTTPException(status_code=404, detail=str(e))
    await service.commit_changes()
    return template


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> Response:
    service = TemplateService(db)

    try:
        await service.delete_template(template_id)
    except TemplateNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    await service.commit_changes()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
