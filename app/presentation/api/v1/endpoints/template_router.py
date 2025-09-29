from io import BytesIO
from typing import Annotated, List, Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from application.exporter.exceptions import (
    ObjectTemplateExportApplicationException,
)
from application.exporter.interactors import ObjectTemplateExportInteractor
from application.importer.dto import OTImportRequestDTO
from application.importer.exceptions import (
    ObjectTemplateImportApplicationException,
)
from application.importer.interactors import (
    ObjectTemplateImportInteractor,
    ObjectTemplateImportValidationInteractor,
)
from application.template.read.exceptions import (
    TemplateReaderApplicationException,
)
from application.template.read.interactors import TemplateReaderInteractor
from application.template.update.exceptions import (
    TemplateUpdaterApplicationException,
)
from application.template.update.interactors import TemplateUpdaterInteractor
from di import get_async_session
from exceptions import (
    TemplateNotFound,
)
from presentation.api.v1.endpoints.dto import (
    TemplateExportRequest,
    TemplateRequest,
    TemplateResponse,
    TemplateResponseDate,
    TemplateUpdateDataInput,
    TemplateUpdateResponse,
)
from presentation.security.security_data_models import UserData
from presentation.security.security_factory import security
from schemas.template_schemas import (
    SimpleTemplateOutput,
)
from services.template_services import TemplateService

router = APIRouter(tags=["template"])


@router.get("/templates")
async def get_templates(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[UserData, Depends(security)],
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
@inject
async def get_templates_by_filter(
    request: TemplateRequest,
    interactor: FromDishka[TemplateReaderInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> TemplateResponse:
    try:
        result = await interactor(request=request.to_interactor_dto())
        output_data: list[TemplateResponseDate] = list()
        for application_el in result.data:
            el = TemplateResponseDate.from_application_dto(application_el)
            output_data.append(el)
        return TemplateResponse(data=output_data)
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateReaderApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.put(
    "/templates/{template_id}",
    status_code=status.HTTP_200_OK,
    response_model=TemplateUpdateResponse,
)
@inject
async def update_template(
    template_id: int,
    template_data: Annotated[
        TemplateUpdateDataInput,
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
    interactor: FromDishka[TemplateUpdaterInteractor],
    user_data: Annotated[UserData, Depends(security)],
) -> TemplateUpdateResponse:
    try:
        result = await interactor(
            request=template_data.to_interactor_dto(template_id)
        )
        output = TemplateUpdateResponse.from_application_dto(result)
        return output
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except TemplateUpdaterApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_template(
    template_id: int,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user_data: Annotated[UserData, Depends(security)],
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


@router.post("/templates/export", status_code=status.HTTP_200_OK)
@inject
async def export_templates(
    template_data: TemplateExportRequest,
    interactor: FromDishka[ObjectTemplateExportInteractor],
    user_data: Annotated[UserData, Depends(security)],
):
    try:
        result = await interactor(request=template_data.to_interactor_dto())
        return StreamingResponse(
            BytesIO(result.excel_file.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except ObjectTemplateExportApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.post("/templates/validate", status_code=status.HTTP_201_CREATED)
@inject
async def import_templates_validate(
    file: Annotated[UploadFile, File],
    interactor: FromDishka[ObjectTemplateImportValidationInteractor],
    user_data: Annotated[UserData, Depends(security)],
):
    try:
        if not file.filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File must be an Excel spreadsheet",
            )
        file_content = await file.read()

        request = OTImportRequestDTO(
            file_data=file_content, owner=user_data.name
        )
        result = await interactor(request=request)
        print(result)
        return []
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except ObjectTemplateImportApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )


@router.post("/templates/import", status_code=status.HTTP_201_CREATED)
@inject
async def import_templates(
    file: Annotated[UploadFile, File],
    interactor: FromDishka[ObjectTemplateImportInteractor],
    user_data: Annotated[UserData, Depends(security)],
):
    try:
        if not file.filename.endswith(".xlsx"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File must be an Excel spreadsheet",
            )
        file_content = await file.read()

        request = OTImportRequestDTO(
            file_data=file_content, owner=user_data.name
        )
        result = await interactor(request=request)
        print(result)
        return []
    except ValidationError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ex.errors()
        )
    except ObjectTemplateImportApplicationException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        print(type(ex), ex)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ex)
        )
