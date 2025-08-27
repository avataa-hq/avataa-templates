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
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)
from infrastructure.db.shared.consts import GATEWAY_ERROR
from infrastructure.db.template_parameter.read.mappers import (
    sql_to_domain,
    template_parameter_filter_to_sql_query,
)
from models import TemplateParameter


class SQLTemplateParameterReaderRepository(TemplateParameterReader):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

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
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_id(
        self, template_parameter_id: int
    ) -> TemplateParameterAggregate:
        query = select(TemplateParameter).where(
            TemplateParameter.id == template_parameter_id
        )
        try:
            result = await self.session.execute(query)
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
        except TemplateParameterReaderApplicationException:
            raise
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_ids(
        self, template_parameter_ids: list[int]
    ) -> list[TemplateParameterAggregate]:
        """Add chunk if len template_parameter_ids  more than 500"""
        if len(template_parameter_ids) > 500:
            self.logger.warning("Too much size for template_parameter_ids")
        output: list[TemplateParameterAggregate] = []
        query = select(TemplateParameter).where(
            TemplateParameter.id.in_(template_parameter_ids)
        )
        try:
            result = await self.session.scalars(query)
        except Exception as ex:
            print(type(ex), ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )
        all_template_parameters = result.all()
        for tp in all_template_parameters:
            template = sql_to_domain(tp)
            output.append(template)
        return output

    async def get_by_template_object_ids(
        self, template_object_ids: list[int]
    ) -> list[TemplateParameterAggregate]:
        if len(template_object_ids) > 500:
            self.logger.warning("Too much size for template_object_ids")
        output: list[TemplateParameterAggregate] = []
        query = select(TemplateParameter).where(
            TemplateParameter.template_object_id.in_(template_object_ids)
        )
        try:
            result = await self.session.scalars(query)
        except Exception as ex:
            print(type(ex), ex)
            raise TemplateParameterReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )
        all_template_parameters = result.all()
        for tp in all_template_parameters:
            template = sql_to_domain(tp)
            output.append(template)
        return output
