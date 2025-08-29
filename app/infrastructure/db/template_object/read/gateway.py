from logging import getLogger

from sqlalchemy import BigInteger, Integer, bindparam, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.query import TemplateObjectReader
from domain.template_object.vo.template_object_by_id_filter import (
    TemplateObjectByIdFilter,
)
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from infrastructure.db.shared.consts import GATEWAY_ERROR
from infrastructure.db.template_object.read.mappers import (
    sql_to_domain,
    template_object_by_id_to_sql_query,
    template_object_filter_to_sql_query,
)
from models import TemplateObject


class SQLTemplateObjectReaderRepository(TemplateObjectReader):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    async def get_by_id(
        self, template_object_id: TemplateObjectByIdFilter
    ) -> TemplateObjectAggregate | None:
        base_query = select(TemplateObject)
        filtered_query = template_object_by_id_to_sql_query(
            template_object_id, TemplateObject, base_query
        )
        try:
            result = await self.session.execute(filtered_query)
            template_param = result.scalar_one_or_none()
            if template_param:
                return sql_to_domain(template_param)
            else:
                self.logger.debug(
                    "Template Object with id: %s not found",
                    template_object_id.id.to_raw(),
                )
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

    async def get_tree_by_filter(
        self, db_filter: TemplateObjectFilter
    ) -> list[TemplateObjectAggregate]:
        output: list[TemplateObjectAggregate] = list()
        cte_query = text("""
        WITH RECURSIVE object_tree AS (
            SELECT
                id,
                template_id,
                parent_object_id,
                object_type_id,
                required,
                valid,
                0 as depth,
                CAST(id AS TEXT) as path
            FROM template_object
            WHERE template_id = :template_id
                    AND (:parent_id IS NULL AND parent_object_id IS NULL
                         OR parent_object_id = :parent_id)

            UNION ALL
            SELECT
                tob.id,
                tob.template_id,
                tob.parent_object_id,
                tob.object_type_id,
                tob.required,
                tob.valid,
                ot.depth + 1,
                ot.path || '->' || CAST(tob.id AS TEXT)
            FROM template_object tob
            INNER JOIN object_tree ot ON tob.parent_object_id = ot.id
            WHERE ot.depth < :max_depth - 1
                AND ot.path NOT LIKE '%' || CAST(tob.id AS TEXT) || '%'
            )
        SELECT * FROM object_tree
        ORDER BY depth, parent_object_id NULLS FIRST, id
        """).bindparams(
            bindparam("parent_id", type_=BigInteger),
            bindparam("template_id", type_=Integer),
            bindparam("max_depth", type_=Integer),
        )
        result = await self.session.execute(
            cte_query,
            {
                "template_id": db_filter.template_object_id,
                "parent_id": db_filter.parent_object_id,
                "max_depth": db_filter.depth,
            },
        )

        for db_el in result.fetchall():  # type: TemplateObject
            template = sql_to_domain(db_el)
            output.append(template)
        return output

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
        query = select(TemplateObject.object_type_id)
        query = query.filter(TemplateObject.id == db_filter.template_object_id)
        try:
            result = await self.session.execute(query)
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
