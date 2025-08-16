from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from domain.template_object.query import TemplateObjectReader
from domain.template_object.template_object import TemplateObjectAggregate
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from infrastructure.db.template_object.read.mappers import (
    sql_to_domain,
    template_object_filter_to_sql_query,
)
from models import TemplateObject


class SQLTemplateObjectReaderRepository(TemplateObjectReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]:
        output: list[TemplateObjectAggregate] = list()
        query = select(TemplateObject)
        query = template_object_filter_to_sql_query(
            db_filter, TemplateObject, query
        )
        try:
            result = await self.session.scalars(query)
            for db_el in result.all():  # type: TemplateObject
                template = sql_to_domain(db_el)
                output.append(template)
            return output

        except Exception as ex:
            print(type(ex), ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail="Gateway Error."
            )
