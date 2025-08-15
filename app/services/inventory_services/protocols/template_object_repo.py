from logging import getLogger
from typing import Sequence

from sqlalchemy import select, update

from domain.template_object.template_object import (
    TemplateObjectAggregate,
)
from models import TemplateObject
from services.common.uow import SQLAlchemyUoW
from services.inventory_services.protocols.utils import (
    handle_db_exceptions,
)


class TemplateObjectRepo(object):
    def __init__(self, session: SQLAlchemyUoW):
        self.session = session
        self.logger = getLogger("Template Object Repo")

    @handle_db_exceptions
    async def set_template_objects_invalid(
        self,
        template_objects: list[TemplateObjectAggregate],
    ) -> list[TemplateObjectAggregate]:
        stmt = (
            update(TemplateObject)
            .where(
                TemplateObject.id.in_(
                    [template.id for template in template_objects]
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
    async def get_template_objects_by_object_type_id(
        self, object_type_ids: list[int]
    ) -> list[TemplateObjectAggregate]:
        stmt = select(TemplateObject).where(
            TemplateObject.object_type_id.in_(object_type_ids)
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
