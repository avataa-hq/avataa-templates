from logging import getLogger

from application.common.uow import UoW
from application.template_parameter.delete.dto import (
    TemplateParameterDeleteRequestDTO,
)
from application.template_parameter.delete.exceptions import (
    TemplateParameterDeleterApplicationException,
)
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from domain.template_parameter.command import TemplateParameterDeleter
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.service import TemplateParameterValidityService


class TemplateParameterDeleterInteractor(object):
    def __init__(
        self,
        tp_reader: TemplateParameterReader,
        tp_deleter: TemplateParameterDeleter,
        tp_validity_service: TemplateParameterValidityService,
        uow: UoW,
    ) -> None:
        self._tp_deleter = tp_deleter
        self._tp_reader = tp_reader
        self._tp_validity_service = tp_validity_service
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterDeleteRequestDTO
    ) -> None:
        try:
            template_parameter = await self._tp_reader.get_by_id(
                request.template_parameter_id
            )
            await self._tp_deleter.delete_template_parameter(
                template_parameter.id
            )
            # Update Validity
            await self._tp_validity_service.validate_after_delete(
                template_parameter.template_object_id.to_raw()
            )
            await self._uow.commit()
            return None
        except TemplateParameterReaderApplicationException as ex:
            self.logger.exception(ex)
            await self._uow.rollback()
            raise TemplateParameterDeleterApplicationException(
                status_code=404,
                detail="Template parameter not found",
            )
        except TemplateParameterDeleterApplicationException as ex:
            self.logger.exception(ex)
            await self._uow.rollback()
            raise
        except Exception as ex:
            await self._uow.rollback()
            self.logger.exception(ex)
            raise TemplateParameterDeleterApplicationException(
                status_code=422,
                detail="Application Error.",
            )
