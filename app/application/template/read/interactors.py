import logging

from application.template.read.dto import (
    TemplateRequestDTO,
    TemplateResponseDataDTO,
    TemplateResponseDTO,
)
from application.template.read.exceptions import (
    TemplateReaderApplicationException,
)
from application.template.read.mapper import template_filter_from_dto
from domain.template.query import TemplateReader
from domain.template.vo.template_filter import TemplateFilter


class TemplateReaderInteractor(object):
    def __init__(self, t_repo: TemplateReader):
        self._repo = t_repo
        self.logger = logging.getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateRequestDTO
    ) -> TemplateResponseDTO:
        template_filters: TemplateFilter = template_filter_from_dto(request)
        try:
            templates = await self._repo.get_template_by_filter(
                template_filters
            )
            # Create user response
            result = TemplateResponseDTO(
                data=[
                    TemplateResponseDataDTO.from_aggregate(el)
                    for el in templates
                ],
            )
            return result

        except TemplateReaderApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateReaderApplicationException(
                status_code=422, detail="Application Error."
            )
