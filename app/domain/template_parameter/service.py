from collections import defaultdict
from logging import getLogger

from application.common.uow import SQLAlchemyUoW
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from domain.common.consts import domain_error_message
from domain.common.exceptions import InvalidValueError
from domain.template.aggregate import TemplateAggregate
from domain.template.command import TemplateUpdater
from domain.template.query import TemplateReader
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.command import TemplateObjectUpdater
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.command import TemplateParameterUpdater
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)
from utils.val_type_validators import validate_by_val_type


class TemplateParameterValidityService:
    def __init__(
        self,
        t_reader: TemplateReader,
        t_updater: TemplateUpdater,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        to_reader: TemplateObjectReader,
        to_updater: TemplateObjectUpdater,
        uow: SQLAlchemyUoW,
    ) -> None:
        self._t_reader = t_reader
        self._t_updater = t_updater
        self._tp_reader = tp_reader
        self._tp_updater = tp_updater
        self._to_reader = to_reader
        self._to_updater = to_updater
        self._uow = uow
        self.logger = getLogger(self.__class__.__name__)

    async def validate(
        self, tprm_id: int, new_val_type: str, multiple: bool
    ) -> None:
        # Check correct valid for 2 stages.
        # Stage 1
        list_template_id_to_update = await self.validate_stage_1(
            tprm_id, new_val_type, multiple
        )

        # Stage 2 Check all TO for template
        if list_template_id_to_update:
            await self.validate_stage_2(list_template_id_to_update)

    async def update_tmo_validity(
        self, template_object: TemplateObjectAggregate
    ) -> bool:
        result = False
        tp_db_filter = TemplateParameterFilter(
            template_object_id=template_object.id,
            limit=512,
            offset=0,
        )
        # Get all exists parameters
        template_parameters = await self._tp_reader.get_by_template_object_id(
            tp_db_filter
        )
        # Check validity
        validity = all((tp.valid for tp in template_parameters))
        if template_object.valid != validity:
            result = True
            template_object.set_valid(validity)
            await self._to_updater.update_template_object(template_object)
        return result

    async def validate_after_delete(self, to_id: int) -> None:
        # Check validity for Parents primary TO
        hierarchy_to = await self._to_reader.get_reverse_tree_by_id(to_id)
        t_to_update: list[int] = list()
        for to in hierarchy_to:
            update_more = await self.update_tmo_validity(to)
            if not update_more:
                break
            t_to_update.append(to.template_id.to_raw())
        else:
            # Check validity for Template
            await self.validate_stage_2(t_to_update)

    async def validate_stage_1(
        self,
        tprm_id: int,
        new_val_type: str,
        multiple: bool,
    ) -> list[int]:
        # Update Template Parameter and Template Object.
        # Return list template id for update
        result: set[int] = set()
        expected_validity: bool = False
        try:
            template_objects_ids = await self._tp_reader.get_template_object_id_by_parameter_type_id(
                tprm_id
            )
            template_objects: list[
                TemplateObjectAggregate
            ] = await self._to_reader.get_by_ids(template_objects_ids)

            template_parameters = (
                await self._tp_reader.get_by_template_object_ids(
                    [to.id.to_raw() for to in template_objects]
                )
            )
            tp_update: list[TemplateParameterAggregate] = []
            by_template_objects = defaultdict(list)
            for parameter in template_parameters:  # type: TemplateParameterAggregate
                if parameter.parameter_type_id.to_raw() == tprm_id:
                    by_template_objects[
                        parameter.template_object_id.to_raw()
                    ].append(parameter)
                    expected_validity = parameter.val_type == new_val_type
                    # Check value corresponds val_type
                    correspond = validate_by_val_type(
                        new_val_type, parameter.value, multiple
                    )
                    expected_validity = correspond and expected_validity
                    if parameter.valid != expected_validity:
                        parameter.set_valid(expected_validity)
                        tp_update.append(parameter)
            # Update bulk for valid for every TP
            if tp_update:
                await self._tp_updater.bulk_update_template_parameter(tp_update)

            # Update tmo by hierarchy
            to_to_update: list[TemplateObjectAggregate] = list()
            # Invalid Template Objects
            for to in template_objects:
                hierarchy_to = await self._to_reader.get_reverse_tree_by_id(
                    to.id.to_raw()
                )
                to_to_update.extend(hierarchy_to)
            if not expected_validity:
                # We should set invalid for all parents
                for to in to_to_update:
                    to.set_valid(expected_validity)
                    await self._to_updater.update_template_object(to)
                    result.add(to.template_id.to_raw())
            else:
                # We should check every parent on validity
                for to in to_to_update:
                    update_more = await self.update_tmo_validity(to)
                    result.add(to.template_id.to_raw())
                    if not update_more:
                        break
            return list(result)

        except TemplateParameterReaderApplicationException:
            raise InvalidValueError(
                status_code=422, detail=domain_error_message
            )
        except TemplateObjectReaderApplicationException:
            raise InvalidValueError(
                status_code=422, detail=domain_error_message
            )

    async def validate_stage_2(
        self, list_template_id_to_update: list[int]
    ) -> None:
        try:
            templates: list[
                TemplateAggregate
            ] = await self._t_reader.get_by_ids(list_template_id_to_update)
            for t in templates:  # type: TemplateAggregate
                raw_validity = (
                    await self._to_reader.get_validity_by_template_id(
                        t.id.to_raw()
                    )
                )
                validity = all(raw_validity)
                if t.valid != validity:
                    t.set_valid(validity)
                    await self._t_updater.update_template(t)
        except TemplateParameterReaderApplicationException:
            raise InvalidValueError(
                status_code=422, detail=domain_error_message
            )
        except TemplateObjectReaderApplicationException:
            raise InvalidValueError(
                status_code=422, detail=domain_error_message
            )

    async def invalid_by_tprm(self, deleted_tprm: list[int]) -> None:
        # Only set invalid by tprm
        # Invalid Template Parameters
        template_parameters = await self._tp_reader.get_by_parameter_type_ids(
            deleted_tprm
        )
        invalid_to: set[int] = set()
        for tp in template_parameters:  # type: TemplateParameterAggregate
            tp.set_valid(False)
            invalid_to.add(tp.template_object_id.to_raw())
        await self._tp_updater.bulk_update_template_parameter(
            template_parameters
        )

        # Invalid Template Objects
        await self.invalid_by_template_object_id(list(invalid_to))

    async def invalid_by_tmo(self, deleted_tmo: list[int]) -> None:
        # Only set invalid by tmo
        # Invalid Template Objects
        template_objects = await self._to_reader.get_by_object_type_ids(
            deleted_tmo
        )
        await self._invalidate_to_and_t(template_objects)

    async def invalid_by_template_object_id(self, to_ids: list[int]) -> None:
        template_objects = await self._to_reader.get_by_ids(to_ids)
        await self._invalidate_to_and_t(template_objects)

    async def _invalidate_to_and_t(
        self, template_objects: list[TemplateObjectAggregate]
    ) -> None:
        to_to_invalid: list[TemplateObjectAggregate] = list()
        # Invalid Template Objects
        for to in template_objects:
            hierarchy_to = await self._to_reader.get_reverse_tree_by_id(
                to.id.to_raw()
            )
            to_to_invalid.extend(hierarchy_to)

        invalid_t_ids: set[int] = set()
        for to in to_to_invalid:
            invalid_t_ids.add(to.template_id.to_raw())
            to.set_valid(False)
            await self._to_updater.update_template_object(to)

        # Invalid Templates
        templates = await self._t_reader.get_by_ids(list(invalid_t_ids))
        for t in templates:
            t.set_valid(False)
            await self._t_updater.update_template(t)
