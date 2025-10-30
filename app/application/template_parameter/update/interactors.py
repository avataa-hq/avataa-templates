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
from domain.template_parameter.service import TemplateParameterValidityService


class TemplateParameterUpdaterInteractor(object):
    def __init__(
        self,
        tp_reader: TemplateParameterReader,
        to_reader: TemplateObjectReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        tp_validity_service: TemplateParameterValidityService,
        uow: UoW,
    ):
        self._tp_reader = tp_reader
        self._to_reader = to_reader
        self._tp_updater = tp_updater
        self._tprm_validator = tprm_validator
        self._tp_validity_service = tp_validity_service
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterUpdateRequestDTO
    ) -> TemplateParameterUpdateDTO:
        update_validity = False
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
            if (
                template_parameter.parameter_type_id
                != validated_data.valid_items[0].parameter_type_id
            ):
                template_parameter.update_parameter_type(
                    validated_data.valid_items[0].parameter_type_id
                )
            if (
                validated_data.valid_items[0].value
                and template_parameter.value
                != validated_data.valid_items[0].value
            ):
                # Auto update to Valid field
                template_parameter.set_value(
                    validated_data.valid_items[0].value
                )
            if (
                validated_data.valid_items[0].required
                and template_parameter.required
                != validated_data.valid_items[0].required
            ):
                template_parameter.set_required_flag(
                    validated_data.valid_items[0].required
                )
            if (
                validated_data.valid_items[0].constraint
                and template_parameter.constraint
                != validated_data.valid_items[0].constraint
            ):
                template_parameter.set_constraint(
                    validated_data.valid_items[0].constraint
                )
            if (
                validated_data.valid_items[0].val_type
                and template_parameter.val_type
                != validated_data.valid_items[0].val_type
            ):
                template_parameter.set_val_type(
                    validated_data.valid_items[0].val_type
                )
                update_validity = True

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
            # Update validity
            if update_validity:
                await self._tp_validity_service.validate(
                    template_parameter.parameter_type_id.to_raw(),
                    template_parameter.val_type,
                    False,
                )
            await self._uow.commit()
            # Update TemplateObject valid

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
        tp_validity_service: TemplateParameterValidityService,
        uow: UoW,
    ):
        self._tp_reader = tp_reader
        self._to_reader = to_reader
        self._tp_updater = tp_updater
        self._tprm_validator = tprm_validator
        self._tp_validity_service = tp_validity_service
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterBulkUpdateRequestDTO
    ) -> list[TemplateParameterUpdateDTO]:
        list_to_update_validity: list[tuple[int, str, bool]] = []
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
            if validated_data.invalid_items or len(
                validated_data.valid_items
            ) != len(request.data):
                raise TemplateParameterUpdaterApplicationException(
                    status_code=422, detail=" ".join(validated_data.errors)
                )
            # Update aggregates
            for parameter, update_data in zip(
                parameters, validated_data.valid_items
            ):
                if parameter.parameter_type_id != update_data.parameter_type_id:
                    parameter.update_parameter_type(
                        update_data.parameter_type_id
                    )
                if update_data.value and update_data.value != parameter.value:
                    # Auto update to Valid field
                    parameter.set_value(update_data.value)
                if (
                    update_data.required
                    and update_data.required != parameter.required
                ):
                    parameter.set_required_flag(update_data.required)
                if (
                    update_data.constraint
                    and update_data.constraint != parameter.constraint
                ):
                    parameter.set_constraint(update_data.constraint)
                if (
                    update_data.val_type
                    and update_data.val_type != parameter.val_type
                ):
                    parameter.set_val_type(update_data.val_type)
                    list_to_update_validity.append(
                        (
                            update_data.parameter_type_id,
                            update_data.val_type,
                            update_data.multiple,
                        )
                    )
            # Bulk save
            await self._tp_updater.bulk_update_template_parameter(parameters)
            # Update validity
            for updating_data in list_to_update_validity:  #  type: tuple[int, str, bool]
                await self._tp_validity_service.validate(
                    updating_data[0], updating_data[1], updating_data[2]
                )
            await self._uow.commit()
            # Create user response
            result = [
                TemplateParameterUpdateDTO.from_aggregate(param)
                for param in parameters
            ]
            return result
        except TemplateParameterUpdaterApplicationException as ex:
            self.logger.exception(ex)
            await self._uow.rollback()
            raise
        except Exception as ex:
            await self._uow.rollback()
            self.logger.exception(ex)
            raise TemplateParameterUpdaterApplicationException(
                status_code=422,
                detail="Application Error.",
            )
