from logging import getLogger
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.template.aggregate import (
    TemplateAggregate,
)
from models import Template
from services.inventory_services.protocols.utils import (
    handle_db_exceptions,
)


class TemplateRepo(object):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = getLogger("Template Repo")

    @handle_db_exceptions
    async def set_templates_invalid(
        self, templates: list[TemplateAggregate]
    ) -> list[TemplateAggregate]:
        stmt = (
            update(Template)
            .where(
                Template.id.in_(
                    [template.id.to_raw() for template in templates]
                )
            )
            .values(valid=False)
            .returning(Template)
        )
        result: Sequence[Template] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [TemplateAggregate.from_db(template) for template in result]
        return []

    @handle_db_exceptions
    async def get_templates_by_id(
        self, template_ids: list[int]
    ) -> list[TemplateAggregate]:
        stmt = select(Template).where(Template.id.in_(template_ids))
        result: Sequence[Template] = (
            await self.session.scalars(statement=stmt)
        ).all()
        if result:
            return [TemplateAggregate.from_db(template) for template in result]
        return []
