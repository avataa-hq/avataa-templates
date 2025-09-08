from logging import getLogger

from application.common.uow import UoW
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from application.template_parameter.update.dto import (
    TemplateParameterBulkUpdateRequestDTO,
    TemplateParameterUpdateDTO,
    TemplateParameterUpdateRequestDTO,
)
from application.template_parameter.update.exceptions import (
    TemplateParameterUpdaterApplicationException,
)
from application.template_parameter.update.mapper import (
    template_parameter_to_validator,
)
from application.tprm_validation.interactors import (
    ParameterValidationInteractor,
)
from domain.template_object.query import TemplateObjectReader
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.command import TemplateParameterUpdater
from domain.template_parameter.query import TemplateParameterReader


class TemplateParameterUpdaterInteractor(object):
    def __init__(
        self,
        tp_reader: TemplateParameterReader,
        to_reader: TemplateObjectReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        uow: UoW,
    ):
        self._tp_reader = tp_reader
        self._to_reader = to_reader
        self._tp_updater = tp_updater
        self._tprm_validator = tprm_validator
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterUpdateRequestDTO
    ) -> TemplateParameterUpdateDTO:
        try:
            # Get parameter
            template_parameter: TemplateParameterAggregate = (
                await self._tp_reader.get_by_id(
                    template_parameter_id=request.id
                )
            )
            # Get info about template object type id
            template_object_filter = TemplateObjectFilter(
                template_object_id=template_parameter.template_object_id.to_raw()
            )
            template_object_type_id = (
                await self._to_reader.get_object_type_by_id(
                    db_filter=template_object_filter
                )
            )

            # Validate parameter
            validation_data = template_parameter_to_validator(
                obj_type_id=template_object_type_id, data=[request]
            )
            validated_data = await self._tprm_validator(request=validation_data)
            if validated_data.invalid_items:
                raise TemplateParameterUpdaterApplicationException(
                    status_code=422, detail=" ".join(validated_data.errors)
                )
            # Update Aggregate
            template_parameter.update_parameter_type(request.parameter_type_id)
            template_parameter.set_value(request.value)
            template_parameter.set_required_flag(request.required)
            template_parameter.set_constraint(request.constraint)

            # Update in DB
            try:
                await self._tp_updater.update_template_parameter(
                    template_parameter
                )
            except TemplateParameterUpdaterApplicationException as ex:
                await self._uow.rollback()
                raise TemplateParameterUpdaterApplicationException(
                    status_code=ex.status_code, detail=ex.detail
                )
            await self._uow.commit()
            # Create user response
            result = TemplateParameterUpdateDTO.from_aggregate(
                template_parameter
            )
            return result

        except TemplateParameterReaderApplicationException as ex:
            await self._uow.rollback()
            raise TemplateParameterUpdaterApplicationException(
                status_code=ex.status_code,
                detail=ex.detail,
            )
        except TemplateParameterUpdaterApplicationException:
            await self._uow.rollback()
            raise
        except Exception as ex:
            await self._uow.rollback()
            self.logger.exception(ex)
            raise TemplateParameterUpdaterApplicationException(
                status_code=422,
                detail="Application Error.",
            )


class BulkTemplateParameterUpdaterInteractor(object):
    def __init__(
        self,
        tp_reader: TemplateParameterReader,
        to_reader: TemplateObjectReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        uow: UoW,
    ):
        self._tp_reader = tp_reader
        self._to_reader = to_reader
        self._tp_updater = tp_updater
        self._tprm_validator = tprm_validator
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterBulkUpdateRequestDTO
    ) -> list:
        try:
            # Get all parameters
            parameters = await self._tp_reader.get_by_ids(
                [template.id for template in request.data]
            )
            if len(request.data) != len(parameters):
                raise TemplateParameterUpdaterApplicationException(
                    status_code=422, detail="Inconsistent parameters."
                )
            # Get info about template object type id
            template_object_filter = TemplateObjectFilter(
                template_object_id=request.template_object_id
            )
            template_object_type_id = (
                await self._to_reader.get_object_type_by_id(
                    db_filter=template_object_filter
                )
            )
            # Validate parameters
            validation_data = template_parameter_to_validator(
                obj_type_id=template_object_type_id, data=request.data
            )
            validated_data = await self._tprm_validator(request=validation_data)
            if validated_data.invalid_items:
                raise TemplateParameterUpdaterApplicationException(
                    status_code=422, detail=" ".join(validated_data.errors)
                )
            # Update aggregates
            for parameter, update_data in zip(parameters, request.data):
                parameter.set_value(update_data.value)
                parameter.set_required_flag(update_data.required)
                parameter.set_constraint(update_data.constraint)
            # Bulk save
            await self._tp_updater.bulk_update_template_parameter(parameters)
            await self._uow.commit()
            # Create user response
            result = [
                TemplateParameterUpdateDTO.from_aggregate(param)
                for param in parameters
            ]
            return result
        except TemplateParameterUpdaterApplicationException:
            await self._uow.rollback()
            raise
        except Exception as ex:
            await self._uow.rollback()
            print(type(ex), ex)
            raise TemplateParameterUpdaterApplicationException(
                status_code=422,
                detail="Application Error.",
            )
