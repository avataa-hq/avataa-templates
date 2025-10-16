from logging import getLogger

from application.common.uow import SQLAlchemyUoW
from application.template.read.exceptions import (
    TemplateReaderApplicationException,
)
from application.template.update.dto import (
    TemplateDataUpdateRequestDTO,
    TemplateUpdateResponseDTO,
)
from application.template.update.exceptions import (
    TemplateUpdaterApplicationException,
)
from application.tmo_validation.dto import TemplateObjectValidationRequestDTO
from application.tmo_validation.exceptions import TMOValidationException
from application.tmo_validation.interactors import TMOValidationInteractor
from domain.template.command import TemplateUpdater
from domain.template.query import TemplateReader


class TemplateUpdaterInteractor(object):
    def __init__(
        self,
        tmo_validator: TMOValidationInteractor,
        t_reader: TemplateReader,
        t_updater: TemplateUpdater,
        uow: SQLAlchemyUoW,
    ):
        self._tmo_validator = tmo_validator
        self._t_reader = t_reader
        self._t_updater = t_updater
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateDataUpdateRequestDTO
    ) -> TemplateUpdateResponseDTO:
        # Get template Aggregate
        try:
            template = await self._t_reader.get_by_id(request.id)
            # Validate object type (exists TMO)
            if template.object_type_id.to_raw() != request.object_type_id:
                validation_request = TemplateObjectValidationRequestDTO(
                    object_type_id=request.object_type_id,
                    parent_object_type_id=None,
                )
                try:
                    await self._tmo_validator(request=validation_request)
                except TMOValidationException as ex:
                    self.logger.exception(ex)
                    raise TemplateUpdaterApplicationException(
                        status_code=ex.status_code, detail=ex.detail
                    )

            # Update aggregate
            template.update_object_type_id(request.object_type_id)
            template.update_name(request.name)
            template.update_owner(request.owner)
            template.update_version()

            # Update in DB
            updated_template = await self._t_updater.update_template(template)
            await self._uow.commit()
            # Create user response
            result = TemplateUpdateResponseDTO.from_aggregate(updated_template)
            return result

        except TemplateReaderApplicationException as ex:
            self.logger.error(ex)
            raise TemplateUpdaterApplicationException(
                status_code=ex.status_code,
                detail=ex.detail,
            )
        except TemplateUpdaterApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateUpdaterApplicationException(
                status_code=422, detail="Application Error."
            )
