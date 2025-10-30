from logging import getLogger
from typing import cast

from sqlalchemy import CursorResult, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.delete.exceptions import (
    TemplateObjectDeleterApplicationException,
)
from domain.template_object.command import TemplateObjectDeleter
from models import TemplateObject


class SQLTemplateObjectDeleterRepository(TemplateObjectDeleter):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.logger = getLogger(self.__class__.__name__)

    async def delete_template_object(self, template_object_id: int) -> None:
        query = delete(TemplateObject)
        query = query.where(TemplateObject.id == template_object_id)
        try:
            result = await self._session.execute(query)
            # Bug https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#change-0651b868cdc88d28c57469affceaf05f
            result = cast(CursorResult, result)
            self.logger.debug(f"Deleted rows: {result.rowcount}.")
        except SQLAlchemyError as ex:
            self.logger.exception(ex)
            raise TemplateObjectDeleterApplicationException(
                status_code=422, detail="Gateway SQL Error."
            )
        except Exception as ex:
            self.logger.exception(ex)
            raise TemplateObjectDeleterApplicationException(
                status_code=422, detail="Gateway Error."
            )
