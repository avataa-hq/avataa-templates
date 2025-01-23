from typing import Sequence
from logging import getLogger

from sqlalchemy import select, update

from domain.template.entities.template import (
    TemplateDTO,
)
from models import Template
from services.common.uow import SQLAlchemyUoW
from services.inventory_services.protocols.utils import (
    handle_db_exceptions,
)


class TemplateRepo(object):
    def __init__(self, session: SQLAlchemyUoW):
        self.session = session
        self.logger = getLogger("Template Repo")

    @handle_db_exceptions
    async def set_templates_invalid(
        self, templates: list[TemplateDTO]
    ) -> list[TemplateDTO]:
        stmt = (
            update(Template)
            .where(Template.id.in_([template.id for template in templates]))
            .values(valid=False)
            .returning(Template)
        )
        result: Sequence[Template] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [TemplateDTO.from_db(template) for template in result]
        return []

    @handle_db_exceptions
    async def get_templates_by_tmo_id(
        self, object_type_ids: list[int]
    ) -> list[TemplateDTO]:
        stmt = select(Template).where(
            Template.object_type_id.in_(object_type_ids)
        )
        result: Sequence[Template] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [TemplateDTO.from_db(template) for template in result]
        return []
