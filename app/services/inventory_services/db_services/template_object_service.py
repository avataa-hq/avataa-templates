from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from services.inventory_services.protocols import (
    TemplateObjectRepo,
    TemplateRepo,
)


class TemplateObjectService(object):
    def __init__(self, session: AsyncSession):
        self.template_repo = TemplateRepo(session=session)
        self.template_object_repo = TemplateObjectRepo(session=session)
        self.logger = getLogger("Template Parameter Service")

    async def set_template_object_invalid(self, tmo_ids: list[int]) -> None:
        try:
            # Invalid objects
            template_objects = (
                await self.template_object_repo.get_template_objects_by_id(
                    object_type_ids=tmo_ids
                )
            )
            await self.template_object_repo.set_template_objects_invalid(
                template_objects=template_objects
            )
            # Invalid templates
            templates = await self.template_repo.get_templates_by_id(
                ids=tmo_ids
            )
            await self.template_repo.set_templates_invalid(templates=templates)
        except ValueError as ex:
            msg = f"{ex} with ids {tmo_ids}"
            self.logger.error(msg=msg)
            raise ValueError(msg)
        except Exception as ex:
            self.logger.error(msg=f"Data rollback. {ex}.")
            raise
