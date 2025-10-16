from collections import defaultdict
from logging import getLogger

from application.template_object.read.dto import (
    TemplateObjectByIdRequestDTO,
    TemplateObjectByObjectTypeRequestDTO,
    TemplateObjectRequestDTO,
    TemplateObjectSearchDTO,
    TemplateObjectWithChildrenSearchDTO,
)
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_object.read.mapper import (
    template_object_by_id_from_dto,
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
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateObjectRequestDTO
    ) -> list[TemplateObjectWithChildrenSearchDTO]:
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
            result = [
                TemplateObjectWithChildrenSearchDTO.from_tree_aggregate(
                    tree=el, parameters=parameters_by_object_id
                )
                for el in tree
            ]

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
    ) -> list[TemplateObjectAggregate]:
        by_parent: dict[int, list[TemplateObjectAggregate]] = defaultdict(list)
        roots: list = []

        for t_obj in flat_objects:
            if t_obj.parent_object_id is None:
                roots.append(t_obj)
            else:
                if t_obj.parent_object_id not in by_parent:
                    by_parent[t_obj.parent_object_id] = []
                by_parent[t_obj.parent_object_id].append(t_obj)

        def assign_children(to):
            to.children = by_parent.get(to.id.to_raw(), [])
            for child in to.children:
                assign_children(child)

        for root in roots:
            assign_children(root)

        return roots


class TemplateObjectByIdReaderInteractor(object):
    def __init__(
        self,
        to_repo: TemplateObjectReader,
        tp_repo: TemplateParameterReader,
    ):
        self._to_repository = to_repo
        self._tp_repository = tp_repo
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateObjectByIdRequestDTO
    ) -> TemplateObjectSearchDTO:
        template_objects_filters = template_object_by_id_from_dto(request)
        try:
            template_object = await self._to_repository.get_by_id(
                template_objects_filters
            )
            if request.include_parameters:
                template_parameters = (
                    await self._tp_repository.get_by_template_object_ids(
                        [template_object.id.to_raw()]
                    )
                )
            else:
                template_parameters = []
            return TemplateObjectSearchDTO.from_aggregate(
                template_object, template_parameters
            )
        except TemplateObjectReaderApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail="Application Error."
            )


class TemplateObjectByObjectTypeReaderInteractor(object):
    def __init__(
        self,
        to_repo: TemplateObjectReader,
    ) -> None:
        self._to_repository = to_repo
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateObjectByObjectTypeRequestDTO
    ) -> list[TemplateObjectSearchDTO]:
        template_objects = await self._to_repository.get_by_object_type_ids(
            [request.object_type_id]
        )

        result = [
            TemplateObjectSearchDTO.from_aggregate(aggregate=el, parameters=[])
            for el in template_objects
        ]
        return result
