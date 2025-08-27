from collections import defaultdict
from logging import getLogger

from application.template_object.read.dto import (
    TemplateObjectRequestDTO,
    TemplateObjectSearchDTO,
)
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_object.read.mapper import (
    template_object_filter_from_dto,
)
from application.template_parameter.read.dto import TemplateParameterSearchDTO
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.query import TemplateParameterReader


class TemplateObjectReaderInteractor(object):
    def __init__(
        self,
        to_repo: TemplateObjectReader,
        tp_repo: TemplateParameterReader,
    ):
        self._to_repository = to_repo
        self._tp_repository = tp_repo
        self.logger = getLogger("TemplateObjectReaderInteractor")

    async def __call__(
        self, request: TemplateObjectRequestDTO
    ) -> TemplateObjectSearchDTO:
        template_objects_filters = template_object_filter_from_dto(request)
        try:
            template_objects = await self._to_repository.get_tree_by_filter(
                template_objects_filters
            )
            tree = self._build_tree_from_flat_list(template_objects)
            if request.include_parameters:
                template_parameters = (
                    await self._tp_repository.get_by_template_object_ids(
                        [to.id.to_raw() for to in template_objects]
                    )
                )
            else:
                template_parameters = []
            parameters_by_object_id: dict[
                int, list[TemplateParameterSearchDTO]
            ] = defaultdict(list)

            for param in template_parameters:
                obj_id = param.template_object_id.to_raw()
                parameters_by_object_id[obj_id].append(
                    TemplateParameterSearchDTO.from_aggregate(param)
                )
            result = TemplateObjectSearchDTO.from_tree_aggregate(
                tree=tree, parameters=parameters_by_object_id
            )

            return result
        except TemplateObjectReaderApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail="Application Error."
            )

    @staticmethod
    def _build_tree_from_flat_list(
        flat_objects: list[TemplateObjectAggregate],
    ) -> TemplateObjectAggregate:
        by_parent: dict[int, list[TemplateObjectAggregate]] = defaultdict(list)
        root: TemplateObjectAggregate | None = None

        for to in flat_objects:  # type: TemplateObjectAggregate
            if to.parent_object_id is None:
                root = to
            else:
                by_parent[to.parent_object_id].append(to)

        def assign_children(obj):
            obj.children = by_parent.get(obj.id.to_raw(), [])
            for child in obj.children:
                assign_children(child)

        if not root:
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail="No root objects found."
            )
        assign_children(root)
        return root
