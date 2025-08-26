from logging import getLogger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_parameter.update.exceptions import (
    TemplateParameterUpdaterApplicationException,
)
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.command import TemplateParameterUpdater
from infrastructure.db.template_parameter.update.mappers import domain_to_sql


class SQLTemplateParameterUpdaterRepository(TemplateParameterUpdater):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    async def update_template_parameters(
        self, template_parameter: TemplateParameterAggregate
    ) -> TemplateParameterAggregate:
        db_model = domain_to_sql(template_parameter)
        try:
            await self.session.merge(db_model)
        except SQLAlchemyError as ex:
            self.logger.exception(ex)
            raise TemplateParameterUpdaterApplicationException(
                status_code=422, detail="Gateway SQL Error."
            )
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterUpdaterApplicationException(
                status_code=422, detail="Gateway Error."
            )
        return template_parameter
