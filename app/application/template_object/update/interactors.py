from logging import getLogger

from application.common.uow import SQLAlchemyUoW
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_object.update.dto import (
    TemplateObjectDataUpdateRequestDTO,
    TemplateObjectUpdateDTO,
)
from application.template_object.update.exceptions import (
    TemplateObjectUpdaterApplicationException,
)
from application.tmo_validation.dto import TemplateObjectValidationRequestDTO
from application.tmo_validation.exceptions import TMOValidationException
from application.tmo_validation.interactors import TMOValidationInteractor
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.command import TemplateObjectUpdater
from domain.template_object.query import TemplateObjectReader
from domain.template_object.vo.template_object_by_id_filter import (
    TemplateObjectByIdFilter,
)


class TemplateObjectUpdaterInteractor(object):
    def __init__(
        self,
        tmo_validator: TMOValidationInteractor,
        to_reader: TemplateObjectReader,
        to_updater: TemplateObjectUpdater,
        uow: SQLAlchemyUoW,
    ):
        self._tmo_validator = tmo_validator
        self._to_reader = to_reader
        self._to_updater = to_updater
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateObjectDataUpdateRequestDTO
    ) -> TemplateObjectUpdateDTO:
        to_id = TemplateObjectByIdFilter(
            id=TemplateObjectId(request.template_object_id)
        )
        try:
            template_object = await self._to_reader.get_by_id(
                template_object_id=to_id
            )

            # Check change hierarchy
            if (
                request.parent_object_id
                and request.parent_object_id != template_object.parent_object_id
            ):
                self.logger.info("Should update hierarch")
                try:
                    parent_to_id = TemplateObjectByIdFilter(
                        id=TemplateObjectId(request.parent_object_id)
                    )
                    parent_object = await self._to_reader.get_by_id(
                        template_object_id=parent_to_id
                    )
                except TemplateObjectReaderApplicationException as ex:
                    self.logger.exception(ex)
                    raise TemplateObjectUpdaterApplicationException(
                        status_code=ex.status_code,
                        detail="Not found Parent Object",
                    )

                validation_request = TemplateObjectValidationRequestDTO(
                    object_type_id=template_object.object_type_id.to_raw(),
                    parent_object_type_id=parent_object.object_type_id.to_raw(),
                )
                try:
                    await self._tmo_validator(request=validation_request)
                except TMOValidationException as ex:
                    self.logger.exception(ex)
                    raise TemplateObjectUpdaterApplicationException(
                        status_code=ex.status_code, detail=ex.detail
                    )
            # Update Aggregate
            template_object.update_parent_object_id(request.parent_object_id)
            template_object.update_required(request.required)

            # Update in DB
            await self._to_updater.update_template_object(
                template_object=template_object
            )
            await self._uow.commit()
            # Create user response
            result = TemplateObjectUpdateDTO.from_aggregate(template_object)
            return result

        except TemplateObjectReaderApplicationException as ex:
            await self._uow.rollback()
            raise TemplateObjectUpdaterApplicationException(
                status_code=ex.status_code, detail=ex.detail
            )
        except TemplateObjectUpdaterApplicationException as ex:
            await self._uow.rollback()
            self.logger.error(ex)
            raise
        except Exception as ex:
            await self._uow.rollback()
            self.logger.error(ex)
            raise TemplateObjectUpdaterApplicationException(
                status_code=422, detail="Application Error."
            )
