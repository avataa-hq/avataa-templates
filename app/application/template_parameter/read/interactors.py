from logging import getLogger

from application.template_parameter.read.dto import (
    TemplateParameterRequestDTO,
    TemplateParameterSearchDTO,
)
from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from application.template_parameter.read.mapper import (
    template_parameter_filter_from_dto,
)
from domain.template_parameter.query import TemplateParameterReader


class TemplateParameterReaderInteractor(object):
    def __init__(self, tp_repo: TemplateParameterReader):
        self._repo = tp_repo
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterRequestDTO
    ) -> list[TemplateParameterSearchDTO]:
        template_parameter_filters = template_parameter_filter_from_dto(request)
        try:
            template_parameters = await self._repo.get_by_template_object_id(
                template_parameter_filters
            )
            # Create user response
            result = [
                TemplateParameterSearchDTO.from_aggregate(el)
                for el in template_parameters
            ]
            return result
        except TemplateParameterReaderApplicationException as ex:
            self.logger.exception(ex)
            raise
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail="Application Error."
            )
