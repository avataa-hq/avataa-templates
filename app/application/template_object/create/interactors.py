from logging import getLogger

from application.common.uow import UoW


class TemplateObjectCreatorInteractor(object):
    def __init__(self, uow: UoW):
        self._uow = uow

        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request) -> list:
        self.logger.info(request)
        # Create Template Object

        # Create Template Parameter
        return []
