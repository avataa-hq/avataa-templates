from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from domain.template_object.aggregate import TemplateObjectAggregate
from services.inventory_services.protocols import (
    TemplateObjectRepo,
    TemplateRepo,
)


class TemplateObjectService(object):
    def __init__(self, session: AsyncSession):
        self.template_repo = TemplateRepo(session=session)
        self.template_object_repo = TemplateObjectRepo(session=session)
        self.logger = getLogger(self.__class__.__name__)

    async def set_template_object_invalid(self, tmo_ids: list[int]) -> None:
        try:
            # Invalid objects
            template_objects: list[
                TemplateObjectAggregate
            ] = await self.template_object_repo.get_template_objects_by_tmo_ids(
                tmo_ids=tmo_ids
            )
            if not template_objects:
                return
            await self.template_object_repo.set_template_objects_invalid(
                template_objects=template_objects
            )
            # Invalid templates
            templates = await self.template_repo.get_templates_by_ids(
                ids=list({to.template_id.to_raw() for to in template_objects})
            )
            await self.template_repo.set_templates_invalid(templates=templates)
        except ValueError as ex:
            msg = f"{ex} with ids {tmo_ids}"
            self.logger.error(msg=msg)
            raise ValueError(msg)
        except Exception as ex:
            self.logger.error(msg=f"Data rollback. {ex}.")
            raise
