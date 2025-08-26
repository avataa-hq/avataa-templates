from logging import getLogger

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.command import TemplateParameterCreator
from domain.template_parameter.vo.template_parameter_create import (
    TemplateParameterCreate,
)
from infrastructure.db.template_parameter.create.mappers import sql_to_domain
from models import TemplateParameter


class SQLTemplateParameterCreatorRepository(TemplateParameterCreator):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    async def create_template_parameters(
        self, create_dtos: list[TemplateParameterCreate]
    ) -> list[TemplateParameterAggregate]:
        output: list[TemplateParameterAggregate] = list()
        data = [
            {
                "template_object_id": dto.template_object_id,
                "parameter_type_id": dto.parameter_type_id,
                "value": dto.value,
                "constraint": dto.constraint,
                "val_type": dto.val_type,
                "required": dto.required,
            }
            for dto in create_dtos
        ]
        stmt = (
            insert(TemplateParameter).values(data).returning(TemplateParameter)
        )
        result = await self.session.execute(stmt)

        for db_el in result.scalars().all():  # type: TemplateParameter
            template_parameter = sql_to_domain(db_el)
            output.append(template_parameter)
        return output
