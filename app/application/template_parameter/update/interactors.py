from logging import getLogger

from application.common.uow import UoW
from application.paramater_validation.interactors import (
    ParameterValidationInteractor,
)
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from application.template_parameter.update.dto import (
    TemplateParameterUpdateDTO,
    TemplateParameterUpdateRequestDTO,
)
from application.template_parameter.update.exceptions import (
    TemplateParameterUpdaterApplicationException,
)
from application.template_parameter.update.mapper import (
    template_parameter_to_validator,
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
        self.uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterUpdateRequestDTO
    ) -> TemplateParameterUpdateDTO:
        try:
            template_parameter: TemplateParameterAggregate = (
                await self._tp_reader.get_by_id(
                    template_parameter_id=request.template_parameter_id
                )
            )
            template_object_filter = TemplateObjectFilter(
                template_id=template_parameter.template_object_id.to_raw()
            )
            template_object_type_id = (
                await self._to_reader.get_object_type_by_id(
                    db_filter=template_object_filter
                )
            )

            inventory_request = template_parameter_to_validator(
                obj_type_id=template_object_type_id, data=[request.data]
            )
            # Validate parameter
            validated_data = await self._tprm_validator(
                request=inventory_request
            )
            if validated_data.invalid_items:
                raise TemplateParameterUpdaterApplicationException(
                    status_code=422, detail=" ".join(validated_data.errors)
                )
            # Update Aggregate
            template_parameter.update_parameter_type(
                request.data.parameter_type_id
            )
            template_parameter.set_value(request.data.value)
            template_parameter.set_required_flag(request.data.required)
            template_parameter.set_constraint(request.data.constraint)

            # Update in DB
            try:
                await self._tp_updater.update_template_parameters(
                    template_parameter
                )
            except TemplateParameterUpdaterApplicationException as ex:
                await self.uow.rollback()
                raise TemplateParameterUpdaterApplicationException(
                    status_code=ex.status_code, detail=ex.detail
                )
            await self.uow.commit()
            # Create user response
            result = TemplateParameterUpdateDTO.from_aggregate(
                template_parameter
            )
            return result

        except TemplateParameterReaderApplicationException as ex:
            await self.uow.rollback()
            raise TemplateParameterUpdaterApplicationException(
                status_code=ex.status_code,
                detail=ex.detail,
            )
        except TemplateParameterUpdaterApplicationException:
            await self.uow.rollback()
            raise
        except Exception as ex:
            await self.uow.rollback()
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
        self.uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request) -> list:
        # Get all parameters
        parameter_ids = [
            update.template_parameter_id for update in request.updates
        ]
        parameters = await self._tp_reader.get_by_ids(parameter_ids)
        print(parameters)

        # Validate parameters
        validation_data = [update for update in request.updates]
        print(validation_data)
        # validated_result = await self._tprm_validator(validation_data)
        # print(validated_result)
        return []

    #     if validated_result.invalid_items and request.fail_on_first_error:
    #         raise BulkUpdateValidationException(validated_result.errors)
    #
    #     # Update aggregates
    #     for parameter, update_data in zip(parameters, request.updates):
    #         try:
    #             parameter.update_parameter_type(update_data.parameter_type_id)
    #             parameter.set_value(update_data.value)
    #             parameter.set_required_flag(update_data.required)
    #             parameter.set_constraint(update_data.constraint)
    #
    #             updated_parameters.append(parameter)
    #         except Exception as e:
    #             if request.fail_on_first_error:
    #                 raise
    #             failed_updates.append({
    #                 'parameter_id': update_data.template_parameter_id,
    #                 'error': str(e)
    #             })
    #
    #     # Bulk save
    #     if updated_parameters:
    #         await self._tp_updater.bulk_update(updated_parameters)
    #         await self.uow.commit()
    #
    #     return BulkTemplateParameterUpdateDTO(
    #         updated_parameters=[
    #             TemplateParameterUpdateDTO.from_aggregate(p)
    #             for p in updated_parameters
    #         ],
    #         failed_updates=failed_updates if failed_updates else None
    #     )
    #
    # except Exception as ex:
    #     await self.uow.rollback()
    #     raise
