import logging

from application.template.reader import interfaces
from application.template.reader.dto import (
    TemplateRequestDTO,
    TemplateGatewayRequestDTO,
    TemplateResponseDTO,
)
from application.template.reader.exceptions import TemplateApplicationException
from domain.template.template import TemplateAggregate


class TemplateReaderInteractor(object):
    def __init__(self, gateway: interfaces.TemplateReader):
        self._gateway = gateway
        self.logger = logging.getLogger("TemplateReaderInteractor")

    async def __call__(
        self, request: TemplateRequestDTO
    ) -> TemplateResponseDTO:
        gateway_request: TemplateGatewayRequestDTO = TemplateGatewayRequestDTO(
            name=request.name,
            owner=request.owner,
            object_type_id=request.object_type_id,
            limit=request.limit,
            offset=request.offset,
        )
        try:
            templates = await self._gateway.get_template_by_filter(
                gateway_request
            )
        except TemplateApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateApplicationException(
                status_code=422, detail="Error in application"
            )
        # Create aggregate
        list_aggregate: list[TemplateAggregate] = list()
        for template in templates:
            aggregate = TemplateAggregate.from_dto(template)
            list_aggregate.append(aggregate)

        # Create user response
        result = TemplateResponseDTO(
            data=[el.to_response_dto() for el in list_aggregate],
        )
        return result
