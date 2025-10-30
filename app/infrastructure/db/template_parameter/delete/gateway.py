from logging import getLogger
from typing import cast

from sqlalchemy import CursorResult, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_parameter.delete.exceptions import (
    TemplateParameterDeleterApplicationException,
)
from domain.template_parameter.command import TemplateParameterDeleter
from models import TemplateParameter


class SQLTemplateParameterDeleterRepository(TemplateParameterDeleter):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def delete_template_parameter(
        self, template_parameter_id: int
    ) -> None:
        query = delete(TemplateParameter)
        query = query.where(TemplateParameter.id == template_parameter_id)
        try:
            result = await self._session.execute(query)
            # Bug https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#change-0651b868cdc88d28c57469affceaf05f
            result = cast(CursorResult, result)
            self.logger.debug(f"Deleted rows: {result.rowcount}.")
        except SQLAlchemyError as ex:
            self.logger.exception(ex)
            raise TemplateParameterDeleterApplicationException(
                status_code=422, detail="Gateway SQL Error."
            )
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateParameterDeleterApplicationException(
                status_code=422, detail="Gateway Error."
            )
