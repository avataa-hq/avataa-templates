from logging import getLogger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.update.exceptions import (
    TemplateObjectUpdaterApplicationException,
)
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.command import TemplateObjectUpdater
from infrastructure.db.template_object.update.mappers import domain_to_sql


class SQLTemplateObjectUpdaterRepository(TemplateObjectUpdater):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def update_template_object(
        self, template_object: TemplateObjectAggregate
    ) -> TemplateObjectAggregate:
        db_model = domain_to_sql(template_object)
        try:
            await self._session.merge(db_model)
            return template_object
        except SQLAlchemyError as ex:
            self.logger.exception(ex)
            raise TemplateObjectUpdaterApplicationException(
                status_code=422, detail="Gateway SQL Error."
            )
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateObjectUpdaterApplicationException(
                status_code=422, detail="Gateway Error."
            )
