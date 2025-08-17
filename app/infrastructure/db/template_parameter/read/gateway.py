from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)
from infrastructure.db.template_parameter.read.mappers import (
    sql_to_domain,
    template_parameter_filter_to_sql_query,
)
from models import TemplateParameter


class SQLTemplateParameterReaderRepository(TemplateParameterReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_filter(
        self, db_filter: TemplateParameterFilter
    ) -> list[TemplateParameterAggregate]:
        output: list[TemplateParameterAggregate] = list()
        base_query = select(TemplateParameter)
        filtered_query = template_parameter_filter_to_sql_query(
            db_filter, TemplateParameter, base_query
        )
        try:
            result = await self.session.scalars(filtered_query)
            for db_el in result.all():  # type: TemplateParameter
                template = sql_to_domain(db_el)
                output.append(template)
            return output
        except Exception as ex:
            print(type(ex), ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail="Gateway Error."
            )
