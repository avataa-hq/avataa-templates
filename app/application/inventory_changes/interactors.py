from application.common.uow import SQLAlchemyUoW
from domain.template_parameter.service import TemplateValidityService
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
        t_validity_service: TemplateValidityService,
        uow: SQLAlchemyUoW,
    ):
        self._to_service = to_service
        self._tp_service = tp_service
        self._t_validity_service = t_validity_service
        self._uow = uow

    async def __call__(self, messages: list[tuple[dict, str, str]]):
        try:
            tmo_ids = []
            # Deleted
            # tprm_ids_to_invalid = []
            # Updated
            tprm_ids_to_check = []

            for message, entity_type, operation in messages:
                if entity_type == "TMO":
                    tmo_ids.extend(
                        [el.get("id") for el in message.get("objects", [])]
                    )
                # elif entity_type == "TPRM" and operation == "deleted":
                #     tprm_ids_to_invalid.append([el.get("id") for el in message.get("objects", [])])
                elif entity_type == "TPRM" and operation == "updated":
                    data = {}
                    for el in message.get("objects", []):
                        data["tprm_id"] = el.get("id")
                        data["val_type"] = el.get("val_type")
                    tprm_ids_to_check.append(data)

            tmo_ids = list(set(tmo_ids))
            # tprm_ids_to_invalid = list(set(tprm_ids_to_invalid))

            if tmo_ids:
                await self._to_service.set_template_object_invalid(tmo_ids)

            # if tprm_ids_to_invalid:
            #     await self._tp_service.set_template_parameter_invalid(
            #         tprm_ids_to_invalid
            #     )
            if tprm_ids_to_check:
                for element in tprm_ids_to_check:
                    await self._t_validity_service.validate(
                        element.get("tprm_id"), element.get("val_type")
                    )

            await self._uow.commit()

        except Exception as ex:
            print(f"Error processing inventory changes: {ex}")
            await self._uow.rollback()
            return False
