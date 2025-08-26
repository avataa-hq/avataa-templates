from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.query import TemplateObjectReader
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from infrastructure.db.shared.consts import GATEWAY_ERROR
from infrastructure.db.template_object.read.mappers import (
    sql_to_domain,
    template_object_filter_to_sql_query,
)
from models import TemplateObject


class SQLTemplateObjectReaderRepository(TemplateObjectReader):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    async def get_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]:
        output: list[TemplateObjectAggregate] = list()
        base_query = select(TemplateObject)
        filtered_query = template_object_filter_to_sql_query(
            db_filter, TemplateObject, base_query
        )
        try:
            result = await self.session.scalars(filtered_query)
            for db_el in result.all():  # type: TemplateObject
                template = sql_to_domain(db_el)
                output.append(template)
            return output

        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def exists(self, db_filter: TemplateObjectFilter) -> bool:
        base_query = select(1)
        filtered_query = template_object_filter_to_sql_query(
            db_filter, TemplateObject, base_query
        ).limit(1)
        try:
            result = await self.session.execute(filtered_query)
            return result.scalar_one_or_none() is not None
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_object_type_by_id(
        self, db_filter: TemplateObjectFilter
    ) -> int:
        base_query = select(TemplateObject.object_type_id)
        filtered_query = template_object_filter_to_sql_query(
            db_filter, TemplateObject, base_query
        )
        try:
            result = await self.session.execute(filtered_query)
            object_type_id = result.scalar_one_or_none()
            if object_type_id:
                return object_type_id
            else:
                raise TemplateObjectReaderApplicationException(
                    status_code=404, detail="Template Object not found."
                )
        except TemplateObjectReaderApplicationException:
            raise
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )
