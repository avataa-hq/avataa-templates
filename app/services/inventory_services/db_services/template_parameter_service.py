from logging import getLogger

from services.common.uow import SQLAlchemyUoW
from services.inventory_services.protocols import (
    TemplateRepo,
    TemplateObjectRepo,
    TemplateParameterRepo,
)


class TemplateParameterService(object):
    def __init__(self, uow: SQLAlchemyUoW):
        self.template_repo = TemplateRepo(
            session=uow
        )
        self.template_object_repo = (
            TemplateObjectRepo(session=uow)
        )
        self.template_parameter_repo = (
            TemplateParameterRepo(session=uow)
        )
        self.uow = uow
        self.logger = getLogger(
            "Template Parameter Service"
        )

    async def set_template_parameter_invalid(
        self, tprm_ids: list[int]
    ) -> None:
        try:
            async with self.uow:
                # Invalidate parameters
                template_parameters = await self.template_parameter_repo.get_template_parameters_by_id(
                    parameter_ids=tprm_ids
                )
                await self.template_parameter_repo.set_template_parameters_invalid(
                    parameters=template_parameters
                )
                tmo_ids = [
                    templ.template_object_id
                    for templ in template_parameters
                ]
                # Invalidate objects
                template_objects = await self.template_object_repo.get_template_objects_by_object_type_id(
                    object_type_ids=tmo_ids
                )
                await self.template_object_repo.set_template_objects_invalid(
                    template_objects=template_objects
                )
                # Invalidate templates
                templates = await self.template_repo.get_templates_by_tmo_id(
                    object_type_ids=tmo_ids
                )
                await self.template_repo.set_templates_invalid(
                    templates=templates
                )
            await self.uow.commit()
        except ValueError as ex:
            await self.uow.rollback()
            msg = f"{ex} with ids {tprm_ids}"
            self.logger.error(msg=msg)
            raise ValueError(msg)
        except Exception as ex:
            await self.uow.rollback()
            self.logger.error(
                msg=f"Data rollback. {ex}."
            )
