from logging import getLogger

from infrastructure.db.template.read.gateway import SQLTemplateReaderRepository


class TemplateParameterCreatorInteractor(object):
    def __init__(self, repository: SQLTemplateReaderRepository, uow):
        self.repository = repository
        self.uow = uow
        self.logger = getLogger("TemplateParameterCreatorInteractor")

    async def __call__(self, request):
        async with self.uow:
            raise NotImplementedError()
