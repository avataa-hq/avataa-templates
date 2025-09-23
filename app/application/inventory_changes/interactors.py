from application.common.uow import SQLAlchemyUoW
from domain.template_parameter.service import TemplateParameterValidityService
from services.inventory_services.db_services.template_object_service import (
    TemplateObjectService,
)
from services.inventory_services.db_services.template_parameter_service import (
    TemplateParameterService,
)


class InventoryChangesInteractor(object):
    def __init__(
        self,
        to_service: TemplateObjectService,
        tp_service: TemplateParameterService,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ):
        self._to_service = to_service
        self._tp_service = tp_service
        self._tp_validity_service = tp_validity_service
        self._uow = uow

    async def __call__(self, messages: list[tuple[dict, str, str]]):
        try:
            tmo_ids: set[int] = set()
            # Deleted
            tprm_ids_to_invalid: set[int] = set()
            # Updated
            tprm_ids_to_check = []

            for message, entity_type, operation in messages:
                if entity_type == "TMO":
                    for el in message.get("objects", []):
                        tmo_ids.add(el.get("id"))
                elif entity_type == "TPRM" and operation == "deleted":
                    for el in message.get("objects", []):
                        tprm_ids_to_invalid.add(el.get("id"))
                elif entity_type == "TPRM" and operation == "updated":
                    data = {}
                    for el in message.get("objects", []):
                        data["tprm_id"] = el.get("id")
                        data["val_type"] = el.get("val_type")
                        data["multiple"] = el.get("multiple")
                    tprm_ids_to_check.append(data)

            if tprm_ids_to_check:
                for element in tprm_ids_to_check:
                    await self._tp_validity_service.validate(
                        element.get("tprm_id"),
                        element.get("val_type"),
                        element.get("multiple"),
                    )
            if tprm_ids_to_invalid:
                await self._tp_validity_service.invalid_by_tprm(
                    list(tprm_ids_to_invalid)
                )
            if tmo_ids:
                await self._tp_validity_service.invalid_by_tmo(list(tmo_ids))
            await self._uow.commit()

        except Exception as ex:
            print(f"Error processing inventory changes: {ex}")
            await self._uow.rollback()
            return False
