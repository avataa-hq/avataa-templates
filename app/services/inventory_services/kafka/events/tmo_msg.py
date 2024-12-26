from services.inventory_services.db_services import TemplateObjectService, TemplateParameterService


async def on_delete_tmo(
    msg,
    template_object_service: TemplateObjectService,
    template_parameter_service: TemplateParameterService,
):
    # print(msg, "on delete tmo")
    tmo_ids = {tmo["id"] for tmo in msg["objects"]}
    await template_object_service.set_template_object_invalid(tmo_ids=list(tmo_ids))


async def on_update_tmo(
    msg,
    template_object_service: TemplateObjectService,
    template_parameter_service: TemplateParameterService,
):
    # print(msg, "on update tmo")
    tmo_ids = {tmo["id"] for tmo in msg["objects"]}
    await template_object_service.set_template_object_invalid(tmo_ids=list(tmo_ids))
