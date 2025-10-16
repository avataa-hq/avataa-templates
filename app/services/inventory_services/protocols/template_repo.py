from logging import getLogger

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
        self.logger = getLogger(self.__class__.__name__)

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
        result = (await self.session.scalars(statement=stmt)).all()
        return [TemplateAggregate.from_db(template) for template in result]

    @handle_db_exceptions
    async def get_templates_by_id(
        self, template_ids: list[int]
    ) -> list[TemplateAggregate]:
        stmt = select(Template).where(Template.id.in_(template_ids))
        result = (await self.session.scalars(statement=stmt)).all()
        return [TemplateAggregate.from_db(template) for template in result]

    @handle_db_exceptions
    async def get_templates_by_tmo_ids(
        self, tmo_ids: list[int]
    ) -> list[TemplateAggregate]:
        stmt = select(Template).where(Template.object_type_id.in_(tmo_ids))
        result = (await self.session.scalars(statement=stmt)).all()
        return [TemplateAggregate.from_db(template) for template in result]

    @handle_db_exceptions
    async def get_templates_by_ids(
        self, ids: list[int]
    ) -> list[TemplateAggregate]:
        stmt = select(Template).where(Template.id.in_(ids))
        result = (await self.session.scalars(statement=stmt)).all()
        return [TemplateAggregate.from_db(template) for template in result]
