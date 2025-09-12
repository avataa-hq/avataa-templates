from logging import getLogger

from application.common.uow import UoW
from application.template_object.delete.dto import (
    TemplateObjectDeleteRequestDTO,
)
from application.template_object.delete.exceptions import (
    TemplateObjectDeleterApplicationException,
)
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.command import TemplateObjectDeleter
from domain.template_object.query import TemplateObjectReader
from domain.template_object.vo.template_object_by_id_filter import (
    TemplateObjectByIdFilter,
)
from domain.template_parameter.service import TemplateParameterValidityService


class TemplateObjectDeleterInteractor(object):
    def __init__(
        self,
        to_reader: TemplateObjectReader,
        to_deleter: TemplateObjectDeleter,
        tp_validity_service: TemplateParameterValidityService,
        uow: UoW,
    ):
        self._to_reader = to_reader
        self._to_deleter = to_deleter
        self._tp_validity_service = tp_validity_service
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request: TemplateObjectDeleteRequestDTO) -> None:
        to_filter = TemplateObjectByIdFilter(
            id=TemplateObjectId(request.template_object_id)
        )
        try:
            template_object = await self._to_reader.get_by_id(to_filter)
            await self._to_deleter.delete_template_object(
                template_object.id.to_raw()
            )
            # Update validity
            if template_object.parent_object_id:
                await self._tp_validity_service.validate_after_delete(
                    template_object.parent_object_id
                )
            else:
                await self._tp_validity_service.validate_stage_2(
                    [template_object.template_id.to_raw()]
                )
            await self._uow.commit()
            return None

        except TemplateObjectReaderApplicationException as ex:
            self.logger.exception(ex)
            await self._uow.rollback()
            raise TemplateObjectDeleterApplicationException(
                status_code=404,
                detail="Template object not found",
            )
        except TemplateObjectDeleterApplicationException as ex:
            self.logger.exception(ex)
            await self._uow.rollback()
            raise
        except Exception as ex:
            await self._uow.rollback()
            self.logger.exception(ex)
            raise TemplateObjectDeleterApplicationException(
                status_code=422,
                detail="Application Error.",
            )
