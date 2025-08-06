from typing import (
    Optional,
    Annotated,
)
from fastapi import (
    Body,
    Query,
    status,
    Depends,
    Response,
    APIRouter,
    HTTPException,
)

from application.common.uow import UoW
from presentation.api.depends_stub import Stub
from schemas.template_schemas import (
    TemplateObjectOutput,
    TemplateObjectUpdateInput,
    TemplateObjectUpdateOutput,
)
from services.template_object_services import (
    TemplateObjectService,
)
from exceptions import (
    TemplateNotFound,
    InvalidHierarchy,
    TemplateObjectNotFound,
)

router = APIRouter(tags=["template-object"])


@router.get("/objects")
async def get_template_objects(
    template_id: int,
    db: Annotated[UoW, Depends(Stub(UoW))],
    parent_id: Optional[int] = Query(
        None,
        description="Parent object ID (optional)",
    ),
    depth: int = Query(
        1,
        ge=1,
        description="Depth of children to retrieve (1 by default)",
    ),
    include_parameters: bool = Query(
        False,
        description="Include parameters in the response (default: False)",
    ),
) -> list[TemplateObjectOutput]:
    service = TemplateObjectService(db)

    try:
        return await service.get_template_objects(
            template_id=template_id,
            parent_id=parent_id,
            depth=depth,
            include_parameters=include_parameters,
        )
    except TemplateNotFound:
        raise HTTPException(
            status_code=404,
            detail="Template not found",
        )
    except TemplateObjectNotFound:
        raise HTTPException(
            status_code=404,
            detail="Parent template object not found",
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
