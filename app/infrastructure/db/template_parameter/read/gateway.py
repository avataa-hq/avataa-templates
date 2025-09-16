from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.vo.template_parameter_exists import (
    TemplateParameterExists,
)
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)
from infrastructure.db.shared.consts import GATEWAY_ERROR
from infrastructure.db.template_parameter.read.mappers import (
    sql_to_domain,
    template_parameter_exists_to_sql_query,
    template_parameter_filter_to_sql_query,
)
from models import TemplateParameter


class SQLTemplateParameterReaderRepository(TemplateParameterReader):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def exists(self, db_filter: TemplateParameterExists) -> bool:
        base_query = select(1)
        filtered_query = template_parameter_exists_to_sql_query(
            db_filter, TemplateParameter, base_query
        )
        try:
            result = await self._session.execute(filtered_query)
            return result.scalar_one_or_none() is not None
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_template_object_id(
        self, db_filter: TemplateParameterFilter
    ) -> list[TemplateParameterAggregate]:
        base_query = select(TemplateParameter)
        filtered_query = template_parameter_filter_to_sql_query(
            db_filter, TemplateParameter, base_query
        )
        try:
            result = await self._session.scalars(filtered_query)
            return [sql_to_domain(tp) for tp in result.all()]
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_id(
        self, template_parameter_id: int
    ) -> TemplateParameterAggregate:
        query = select(TemplateParameter)
        query = query.where(TemplateParameter.id == template_parameter_id)
        try:
            result = await self._session.execute(query)
            template_param = result.scalar_one_or_none()
            if template_param:
                return sql_to_domain(template_param)
            else:
                self.logger.debug(
                    "Template Parameter with id: %s not found",
                    template_parameter_id,
                )
                raise TemplateParameterReaderApplicationException(
                    status_code=404, detail="Template Parameter not found."
                )

        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_ids(
        self, template_parameter_ids: list[int]
    ) -> list[TemplateParameterAggregate]:
        query = select(TemplateParameter)
        query = query.where(TemplateParameter.id.in_(template_parameter_ids))
        try:
            result = await self._session.scalars(query)
            return [sql_to_domain(tp) for tp in result.all()]
        except TemplateParameterReaderApplicationException:
            raise
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_filters(
        self, db_filter: TemplateParameterExists
    ) -> list[TemplateParameterAggregate]:
        """Add chunk if len template_parameter_ids  more than 500"""
        if len(db_filter.parameter_type_id) > 500:
            self.logger.warning("Too much size for template_parameter_ids")
        base_query = select(TemplateParameter)
        filtered_query = template_parameter_exists_to_sql_query(
            db_filter, TemplateParameter, base_query
        )
        try:
            result = await self._session.scalars(filtered_query)
            return [sql_to_domain(tp) for tp in result.all()]
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_template_object_ids(
        self, template_object_ids: list[int]
    ) -> list[TemplateParameterAggregate]:
        if len(template_object_ids) > 500:
            self.logger.warning("Too much size for template_object_ids")
        query = select(TemplateParameter)
        query = query.where(
            TemplateParameter.template_object_id.in_(template_object_ids)
        )
        try:
            result = await self._session.scalars(query)
            return [sql_to_domain(tp) for tp in result.all()]
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_parameter_type_ids(
        self, parameter_type_ids: list[int]
    ) -> list[TemplateParameterAggregate]:
        query = select(TemplateParameter)
        query = query.where(
            TemplateParameter.parameter_type_id.in_(parameter_type_ids)
        )
        try:
            result = await self._session.scalars(query)
            return [sql_to_domain(tp) for tp in result.all()]
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_template_object_id_by_parameter_type_id(
        self, parameter_type_id: int
    ) -> list[int]:
        query = select(TemplateParameter.template_object_id)
        query = query.where(
            TemplateParameter.parameter_type_id == parameter_type_id
        )
        try:
            result = await self._session.execute(query)
            return list(result.scalars().all())
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )
