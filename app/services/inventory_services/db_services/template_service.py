from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession

from services.inventory_services.protocols.template_repo import (
    TemplateRepo,
)


class TemplateService(object):
    def __init__(self, session: AsyncSession):
        self.template_service_repo = TemplateRepo(session=session)
        self.logger = getLogger("Template Service")
