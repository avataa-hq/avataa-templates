from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from services.inventory_services.protocols import (
    TemplateObjectRepo,
    TemplateParameterRepo,
    TemplateRepo,
)


class TemplateParameterService(object):
    def __init__(self, session: AsyncSession):
        self.template_repo = TemplateRepo(session=session)
        self.template_object_repo = TemplateObjectRepo(session=session)
        self.template_parameter_repo = TemplateParameterRepo(session=session)

        self.logger = getLogger("Template Parameter Service")

    async def set_template_parameter_invalid(self, tprm_ids: list[int]) -> None:
        try:
            # Invalidate parameters
            template_parameters = await self.template_parameter_repo.get_template_parameters_by_parameter_id(
                parameter_ids=tprm_ids
            )
            if template_parameters:
                await self.template_parameter_repo.set_template_parameters_invalid(
                    parameters=template_parameters
                )
                template_object_ids = [
                    templ.template_object_id.to_raw()
                    for templ in template_parameters
                ]
                if template_object_ids:
                    # Invalidate objects
                    template_objects = await self.template_object_repo.get_template_objects_by_id(
                        ids=template_object_ids
                    )
                    await (
                        self.template_object_repo.set_template_objects_invalid(
                            template_objects=template_objects
                        )
                    )
                    # Invalidate templates
                    templates = await self.template_repo.get_templates_by_id(
                        template_ids=[
                            to.template_id.to_raw() for to in template_objects
                        ]
                    )
                    await self.template_repo.set_templates_invalid(
                        templates=templates
                    )
        except ValueError as ex:
            msg = f"{ex} with ids {tprm_ids}"
            self.logger.error(msg=msg)
            raise ValueError(msg)
        except Exception as ex:
            self.logger.error(msg=f"Data rollback. {ex}.")
            raise
