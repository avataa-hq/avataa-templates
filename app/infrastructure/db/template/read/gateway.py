from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template.read.exceptions import TemplateApplicationException
from domain.template.query import TemplateReader
from domain.template.template import TemplateAggregate
from domain.template.vo.template_filter import TemplateFilter
from infrastructure.db.template.read.mappers import postgres_to_domain
from models import Template


class SQLTemplateRepository(TemplateReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_templates(self):
        raise NotImplementedError

    async def get_template_by_filter(
        self, db_filter: TemplateFilter
    ) -> list[TemplateAggregate]:
        filters = []
        output: list[TemplateAggregate] = list()

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
        try:
            result = await self.session.execute(query)
        except Exception as ex:
            raise TemplateApplicationException(
                status_code=400,
                detail=str(ex),
            )
        for db_el in result.scalars().all():  # type: Template
            template = postgres_to_domain(db_el)
            output.append(template)
        return output
