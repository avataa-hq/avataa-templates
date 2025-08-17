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
    template_parameter_filter_from_dto,
)
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
    ) -> list[TemplateObjectSearchDTO]:
        # Children not implemented
        template_objects_filters = template_object_filter_from_dto(request)
        try:
            template_objects = await self._to_repository.get_by_filter(
                template_objects_filters
            )
            if request.include_parameters:
                template_parameters_filters = (
                    template_parameter_filter_from_dto(request)
                )
                template_parameters = await self._tp_repository.get_by_filter(
                    template_parameters_filters
                )
            else:
                template_parameters = []

            result = [
                TemplateObjectSearchDTO.from_aggregate(
                    aggregate=el, parameters=template_parameters
                )
                for el in template_objects
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
