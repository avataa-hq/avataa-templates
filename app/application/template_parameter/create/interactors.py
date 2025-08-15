from logging import getLogger

from application.common.uow import SQLAlchemyUnitOfWork
from domain.template_parameter.command import TemplateParameterCreator


class TemplateParameterCreatorInteractor(object):
    def __init__(
        self, repository: TemplateParameterCreator, uow: SQLAlchemyUnitOfWork
    ):
        self.repository = repository
        self.uow = uow
        self.logger = getLogger("TemplateParameterCreatorInteractor")

    async def __call__(self, request):
        async with self.uow:
            raise NotImplementedError()
