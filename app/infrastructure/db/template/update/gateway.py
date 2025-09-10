from logging import getLogger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template.update.exceptions import (
    TemplateUpdaterApplicationException,
)
from domain.template.aggregate import TemplateAggregate
from domain.template.command import TemplateUpdater
from infrastructure.db.template.update.mappers import (
    domain_to_sql,
    sql_to_domain,
)


class SQLTemplateUpdaterRepository(TemplateUpdater):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def update_template(
        self, template: TemplateAggregate
    ) -> TemplateAggregate:
        db_model = domain_to_sql(template)
        try:
            db_model = await self._session.merge(db_model)
            await self._session.flush()
            await self._session.refresh(db_model)
            return sql_to_domain(db_model)
        except SQLAlchemyError as ex:
            self.logger.exception(ex)
            raise TemplateUpdaterApplicationException(
                status_code=422, detail="Gateway SQL Error."
            )
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateUpdaterApplicationException(
                status_code=422, detail="Gateway Error."
            )
