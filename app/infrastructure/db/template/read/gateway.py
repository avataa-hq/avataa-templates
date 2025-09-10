from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.template.read.exceptions import (
    TemplateReaderApplicationException,
)
from domain.template.aggregate import TemplateAggregate
from domain.template.query import TemplateReader
from domain.template.vo.template_filter import TemplateFilter
from infrastructure.db.shared.consts import GATEWAY_ERROR
from infrastructure.db.template.read.mappers import (
    sql_to_domain,
    template_to_sql_query,
)
from models import Template


class SQLTemplateReaderRepository(TemplateReader):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def get_all_templates(self):
        raise NotImplementedError

    async def get_template_by_filter(
        self, db_filter: TemplateFilter
    ) -> list[TemplateAggregate]:
        query = select(Template)
        query = template_to_sql_query(db_filter, Template, query)
        try:
            result = await self._session.scalars(query)
            return [sql_to_domain(t) for t in result.all()]
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateReaderApplicationException(
                status_code=400,
                detail=GATEWAY_ERROR,
            )

    async def get_by_id(self, template_id: int) -> TemplateAggregate:
        query = select(Template).where(Template.id == template_id)
        try:
            result = await self._session.execute(query)
            template_param = result.scalar_one_or_none()
            if template_param:
                return sql_to_domain(template_param)
            else:
                self.logger.debug(
                    "Template with id: %s not found",
                    template_id,
                )
                raise TemplateReaderApplicationException(
                    status_code=404, detail="Template not found."
                )
        except TemplateReaderApplicationException:
            raise
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )

    async def get_by_ids(
        self, template_ids: list[int]
    ) -> list[TemplateAggregate]:
        query = select(Template)
        query = query.where(Template.id.in_(template_ids))
        try:
            result = await self._session.scalars(query)
            return [sql_to_domain(to) for to in result.all()]
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateReaderApplicationException(
                status_code=422, detail=GATEWAY_ERROR
            )
