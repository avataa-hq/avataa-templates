from logging import getLogger
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.template_object.aggregate import (
    TemplateObjectAggregate,
)
from models import TemplateObject
from services.inventory_services.protocols.utils import (
    handle_db_exceptions,
)


class TemplateObjectRepo(object):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger(self.__class__.__name__)

    @handle_db_exceptions
    async def set_template_objects_invalid(
        self,
        template_objects: list[TemplateObjectAggregate],
    ) -> list[TemplateObjectAggregate]:
        stmt = (
            update(TemplateObject)
            .where(
                TemplateObject.id.in_(
                    [template.id.to_raw() for template in template_objects]
                )
            )
            .values(valid=False)
            .returning(TemplateObject)
        )
        result: Sequence[TemplateObject] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [
                TemplateObjectAggregate.from_db(template_obj)
                for template_obj in result
            ]
        return []

    @handle_db_exceptions
    async def get_template_objects_by_id(
        self, ids: list[int]
    ) -> list[TemplateObjectAggregate]:
        stmt = select(TemplateObject).where(TemplateObject.id.in_(ids))
        result: Sequence[TemplateObject] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [
                TemplateObjectAggregate.from_db(template_obj)
                for template_obj in result
            ]
        return []

    @handle_db_exceptions
    async def get_template_objects_by_tmo_ids(
        self, tmo_ids: list[int]
    ) -> list[TemplateObjectAggregate]:
        stmt = select(TemplateObject).where(
            TemplateObject.object_type_id.in_(tmo_ids)
        )
        result: Sequence[TemplateObject] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [
                TemplateObjectAggregate.from_db(template_obj)
                for template_obj in result
            ]
        return []
