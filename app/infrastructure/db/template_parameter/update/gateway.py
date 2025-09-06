from logging import getLogger

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_parameter.update.exceptions import (
    TemplateParameterUpdaterApplicationException,
)
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.command import TemplateParameterUpdater
from infrastructure.db.template_parameter.update.mappers import (
    domain_to_bulk_sql,
    domain_to_sql,
)
from models import TemplateParameter


class SQLTemplateParameterUpdaterRepository(TemplateParameterUpdater):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def update_template_parameter(
        self, template_parameter: TemplateParameterAggregate
    ) -> TemplateParameterAggregate:
        db_model = domain_to_sql(template_parameter)
        try:
            await self._session.merge(db_model)
            return template_parameter
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

    async def bulk_update_template_parameter(
        self, template_parameters: list[TemplateParameterAggregate]
    ) -> list[TemplateParameterAggregate]:
        update_data = domain_to_bulk_sql(template_parameters)
        try:
            await self._session.execute(update(TemplateParameter), update_data)
            return template_parameters
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
