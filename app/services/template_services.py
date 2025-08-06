from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.template_schemas import (
    SimpleTemplateOutput,
    TemplateUpdateInput,
    TemplateUpdateOutput,
)
from models import Template
from exceptions import (
    TemplateNotFound,
)
from .template_registry_services import (
    TemplateRegistryService,
)


class TemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_templates(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> List[SimpleTemplateOutput]:
        query = select(Template)

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        result = await self.db.execute(query)
        templates = result.scalars().all()

        return [
            SimpleTemplateOutput(
                id=template.id,
                name=template.name,
                owner=template.owner,
                object_type_id=template.object_type_id,
                valid=template.valid,
            )
            for template in templates
        ]

    async def update_template(
        self,
        template_id: int,
        template_data: TemplateUpdateInput,
    ) -> TemplateUpdateOutput:
        result = await self.db.execute(
            select(Template).filter_by(id=template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise TemplateNotFound

        if template_data.object_type_id != template.object_type_id:
            registry_service = TemplateRegistryService(self.db)
            await registry_service.initialize_hierarchy_map()
            registry_service.validate_object_type(template_data.object_type_id)

        template.object_type_id = template_data.object_type_id
        template.name = template_data.name
        template.owner = template_data.owner

        await self.db.flush()

        return TemplateUpdateOutput(
            id=template.id,
            name=template.name,
            owner=template.owner,
            object_type_id=template.object_type_id,
            valid=template.valid,
        )

    async def delete_template(self, template_id: int) -> None:
        result = await self.db.execute(
            select(Template).filter_by(id=template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise TemplateNotFound

        await self.db.delete(template)

    async def commit_changes(self) -> None:
        await self.db.commit()
