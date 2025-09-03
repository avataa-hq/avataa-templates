from logging import getLogger

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from models import TemplateParameter
from services.inventory_services.protocols.utils import (
    handle_db_exceptions,
)


class TemplateParameterRepo(object):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    @handle_db_exceptions
    async def set_template_parameters_invalid(
        self,
        parameters: list[TemplateParameterAggregate],
    ) -> list[TemplateParameterAggregate]:
        stmt = (
            update(TemplateParameter)
            .where(
                TemplateParameter.id.in_(
                    [parameter.id for parameter in parameters]
                )
            )
            .values(valid=False)
            .returning(TemplateParameter)
        )
        result = (await self.session.scalars(statement=stmt)).all()
        return [TemplateParameterAggregate.from_db(tp) for tp in result]

    @handle_db_exceptions
    async def get_template_parameters_by_parameter_id(
        self, parameter_ids: list[int]
    ) -> list[TemplateParameterAggregate]:
        self.logger.info(
            f"Getting template parameter {parameter_ids} to invalid"
        )
        stmt = select(TemplateParameter).where(
            TemplateParameter.parameter_type_id.in_(parameter_ids)
        )
        result = (await self.session.scalars(statement=stmt)).all()
        return [TemplateParameterAggregate.from_db(tp) for tp in result]
