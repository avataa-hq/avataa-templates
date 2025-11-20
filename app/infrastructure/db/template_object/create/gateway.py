from logging import getLogger

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.command import TemplateObjectCreator
from domain.template_object.vo.template_object_create import (
    TemplateObjectCreate,
)
from infrastructure.db.template_object.create.mappers import sql_to_domain
from models import TemplateObject


class SQLTemplateObjectCreatorRepository(TemplateObjectCreator):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    async def create_template_object(
        self, create_dtos: list[TemplateObjectCreate]
    ) -> list[TemplateObjectAggregate]:
        output: list[TemplateObjectAggregate] = list()
        data = [
            {
                "template_id": dto.template_id.to_raw(),
                "object_type_id": dto.object_type_id.to_raw(),
                "parent_object_id": dto.parent_id.to_raw()
                if dto.parent_id
                else None,
                "required": dto.required,
                "valid": dto.valid,
            }
            for dto in create_dtos
        ]
        stmt = insert(TemplateObject).values(data).returning(TemplateObject)
        result = await self.session.execute(stmt)

        for db_el in result.scalars().all():  # type: TemplateObject
            template_parameter = sql_to_domain(db_el)
            output.append(template_parameter)
        return output
