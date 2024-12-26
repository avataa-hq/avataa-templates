from services.inventory_services.db_services import TemplateObjectService, TemplateParameterService


async def on_delete_tprm(
    msg,
    template_object_service: TemplateObjectService,
    template_parameter_service: TemplateParameterService,
):
    # print(msg, "on delete tprm")
    tprm_ids = {tprm["id"] for tprm in msg["objects"]}
    await template_parameter_service.set_template_parameter_invalid(
        tprm_ids=list(tprm_ids)
    )


async def on_update_tprm(
    msg,
    template_object_service: TemplateObjectService,
    template_parameter_service: TemplateParameterService,
):
    # print(msg, "on update tprm")
    tprm_ids = {tprm["id"] for tprm in msg["objects"]}
    await template_parameter_service.set_template_parameter_invalid(
        tprm_ids=list(tprm_ids)
    )
