from application.common.uow import SQLAlchemyUoW
from services.inventory_services.db_services.template_object_service import (
    TemplateObjectService,
)
from services.inventory_services.db_services.template_parameter_service import (
    TemplateParameterService,
)


class InventoryChangesInteractor(object):
    def __init__(
        self,
        template_object_service: TemplateObjectService,
        template_parameter_service: TemplateParameterService,
        uow: SQLAlchemyUoW,
    ):
        self._to_service = template_object_service
        self._tp_service = template_parameter_service
        self._uow = uow

    async def __call__(self, messages: list):
        try:
            tmo_ids = []
            tprm_ids = []

            for message in messages:
                if message.entity_type == "TMO":
                    tmo_ids.extend(message.entity_ids)
                elif message.entity_type == "TPRM":
                    tprm_ids.extend(message.entity_ids)

            tmo_ids = list(set(tmo_ids))
            tprm_ids = list(set(tprm_ids))

            if tmo_ids:
                await self._to_service.set_template_object_invalid(tmo_ids)

            if tprm_ids:
                await self._tp_service.set_template_parameter_invalid(tprm_ids)

            await self._uow.commit()
            return True

        except Exception as ex:
            print(f"Error processing inventory changes: {ex}")
            await self._uow.rollback()
            return False
