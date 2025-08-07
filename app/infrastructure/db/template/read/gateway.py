from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template.reader.dto import (
    TemplateGatewayRequestDTO,
    TemplateGatewayResponseDTO,
)
from application.template.reader.interfaces import TemplateReader
from models import Template


class SQLTemplateRepository(TemplateReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_templates(self):
        raise NotImplementedError

    async def get_template_by_filter(
        self, db_filter: TemplateGatewayRequestDTO
    ) -> list[TemplateGatewayResponseDTO]:
        filters = []

        if db_filter.name is not None:
            filters.append(Template.name == db_filter.name)
        if db_filter.owner is not None:
            filters.append(Template.owner == db_filter.owner)
        if db_filter.object_type_id is not None:
            filters.append(Template.object_type_id == db_filter.object_type_id)

        query = (
            select(Template)
            .filter(*filters)
            .limit(db_filter.limit)
            .offset(db_filter.offset)
        )

        result = await self.session.execute(query)
        output: list[TemplateGatewayResponseDTO] = list()
        for db_el in result.scalars().all():  # type: Template
            el = TemplateGatewayResponseDTO(
                id=db_el.id,
                name=db_el.name,
                owner=db_el.owner,
                object_type_id=db_el.object_type_id,
                creation_date=db_el.creation_date,
                modification_date=db_el.modification_date,
                valid=db_el.valid,
                version=db_el.version,
            )
            output.append(el)
        return output
