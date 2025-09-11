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


class TemplateValidityService:
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

    async def validate(self, tprm_id: int, new_val_type: str):
        # CHeck correct valid for 2 stages.
        try:
            # Stage 1
            list_template_id_to_update = await self.validate_stage_1(
                tprm_id, new_val_type
            )

            # Stage 2 Check all TO for template
            if list_template_id_to_update:
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

    async def validate_stage_1(
        self, tprm_id: int, new_val_type: str
    ) -> list[int]:
        # Update Template Parameter and Template Object.
        # Return list template id for update
        result: list[int] = []
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
                    if parameter.valid != expected_validity:
                        parameter.set_valid(expected_validity)
                        tp_update.append(parameter)
            # Update bulk for valid for every TP
            if tp_update:
                await self._tp_updater.bulk_update_template_parameter(tp_update)

            # Update TO
            for to in template_objects:  # type: TemplateObjectAggregate
                validity = all(
                    (tp.valid for tp in by_template_objects[to.id.to_raw()])
                )
                if to.valid != validity:
                    to.set_valid(validity)
                    await self._to_updater.update_template_object(to)
                    result.append(to.template_id.to_raw())
            # Update in up tmo
            to_to_update: list[TemplateObjectAggregate] = list()
            # Invalid Template Objects
            for to in template_objects:
                hierarchy_to = await self._to_reader.get_reverse_tree_by_id(
                    to.id.to_raw()
                )
                to_to_update.extend(hierarchy_to)

            for to in to_to_update:
                to.set_valid(expected_validity)
                await self._to_updater.update_template_object(to)
            return result

        except TemplateParameterReaderApplicationException:
            raise InvalidValueError(
                status_code=422, detail=domain_error_message
            )
        except TemplateObjectReaderApplicationException:
            raise InvalidValueError(
                status_code=422, detail=domain_error_message
            )

    async def invalid_by_tprm(self, deleted_tprm: list[int]):
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

    async def invalid_by_tmo(self, deleted_tmo: list[int]):
        # Only set invalid by tmo
        # Invalid Template Objects
        template_objects = await self._to_reader.get_by_object_type_ids(
            deleted_tmo
        )
        await self._invalidate_to_and_t(template_objects)

    async def invalid_by_template_object_id(self, to_ids: list[int]):
        template_objects = await self._to_reader.get_by_ids(to_ids)
        await self._invalidate_to_and_t(template_objects)

    async def _invalidate_to_and_t(
        self, template_objects: list[TemplateObjectAggregate]
    ):
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
