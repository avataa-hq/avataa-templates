from logging import getLogger

from services.inventory_services.protocols.template_repo import (
    TemplateRepo,
)
from services.common.uow import SQLAlchemyUoW


class TemplateService(object):
    def __init__(self, uow: SQLAlchemyUoW):
        self.template_service_repo = TemplateRepo(session=uow)
        self.uow = uow
        self.logger = getLogger("Template Service")
