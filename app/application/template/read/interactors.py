import logging

from application.template.read.dto import (
    TemplateRequestDTO,
    TemplateResponseDataDTO,
    TemplateResponseDTO,
)
from application.template.read.exceptions import TemplateApplicationException
from application.template.read.mapper import template_filter_from_dto
from domain.template.query import TemplateReader
from domain.template.template import TemplateAggregate
from domain.template.vo.template_filter import TemplateFilter


class TemplateReaderInteractor(object):
    def __init__(self, repository: TemplateReader):
        self._repository = repository
        self.logger = logging.getLogger("TemplateReaderInteractor")

    async def __call__(
        self, request: TemplateRequestDTO
    ) -> TemplateResponseDTO:
        template_filters: TemplateFilter = template_filter_from_dto(request)
        try:
            templates: list[
                TemplateAggregate
            ] = await self._repository.get_template_by_filter(template_filters)
        except TemplateApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateApplicationException(
                status_code=422, detail="Application Error."
            )

        # Create user response
        result = TemplateResponseDTO(
            data=[
                TemplateResponseDataDTO.from_aggregate(el) for el in templates
            ],
        )
        return result
