from typing import Annotated, Optional, List
from fastapi import (
    Body,
    Query,
    status,
    Depends,
    Response,
    APIRouter,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas.template_schemas import (
    SimpleTemplateOutput,
    TemplateUpdateInput,
    TemplateUpdateOutput,
)
from services.template_services import (
    TemplateService,
)
from exceptions import (
    TemplateNotFound,
    TMOIdNotFoundInInventory,
)


router = APIRouter(tags=["template"])


@router.get("/templates")
async def get_templates(
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
    db: AsyncSession = Depends(get_session),
) -> List[SimpleTemplateOutput]:
    service = TemplateService(db)
    result = await service.get_templates(
        limit=limit, offset=offset
    )
    return result


@router.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    template_data: Annotated[
        TemplateUpdateInput,
        Body(
            example={
                "name": "Template Name X",
                "owner": "Updated Owner",
                "object_type_id": 1,
            }
        ),
    ],
    db: AsyncSession = Depends(get_session),
) -> TemplateUpdateOutput:
    service = TemplateService(db)

    try:
        template = await service.update_template(
            template_id=template_id,
            template_data=template_data,
        )
    except TemplateNotFound as e:
        raise HTTPException(
            status_code=404, detail=str(e)
        )
    except TMOIdNotFoundInInventory as e:
        raise HTTPException(
            status_code=404, detail=str(e)
        )
    await service.commit_changes()
    return template


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_session),
):
    service = TemplateService(db)

    try:
        await service.delete_template(template_id)
    except TemplateNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )

    await service.commit_changes()
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
