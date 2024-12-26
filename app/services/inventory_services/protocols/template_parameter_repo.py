from typing import Sequence
from logging import getLogger

from sqlalchemy import select, update

from domain.template_parameter.entities.template_parameter import TemplateParameterDTO
from models import TemplateParameter
from services.common.uow import SQLAlchemyUoW
from services.inventory_services.protocols.utils import handle_db_exceptions


class TemplateParameterRepo(object):
    def __init__(self, session: SQLAlchemyUoW):
        self.session = session
        self.logger = getLogger("Template Parameter Repo")

    @handle_db_exceptions
    async def set_template_parameters_invalid(
        self, parameters: list[TemplateParameterDTO]
    ) -> list[TemplateParameterDTO]:
        stmt = (
            update(TemplateParameter)
            .where(TemplateParameter.id.in_([parameter.id for parameter in parameters]))
            .values(valid=False)
            .returning(TemplateParameter)
        )
        result: Sequence[TemplateParameter] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [TemplateParameterDTO.from_db(template) for template in result]
        return []

    @handle_db_exceptions
    async def get_template_parameters_by_id(
        self, parameter_ids: list[int]
    ) -> list[TemplateParameterDTO]:
        self.logger.info(f"Getting template parameter {parameter_ids} to invalid")
        stmt = select(TemplateParameter).where(TemplateParameter.id.in_(parameter_ids))
        result: Sequence[TemplateParameter] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [TemplateParameterDTO.from_db(template) for template in result]
        return []
