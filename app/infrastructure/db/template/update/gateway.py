from logging import getLogger

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template.update.exceptions import (
    TemplateUpdaterApplicationException,
)
from domain.template.aggregate import TemplateAggregate
from domain.template.command import TemplateUpdater
from infrastructure.db.template.update.mappers import (
    domain_to_dict,
    sql_to_domain,
)
from models import Template


class SQLTemplateUpdaterRepository(TemplateUpdater):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def update_template(
        self, template: TemplateAggregate
    ) -> TemplateAggregate:
        db_dict = domain_to_dict(template)
        query = update(Template)
        query = query.where(Template.id == db_dict.get("id"))
        query = query.values(**db_dict)
        query = query.returning(Template)
        try:
            result = await self._session.execute(query)
            db_model = result.scalars().one()
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
