from logging import getLogger


class TemplateParameterUpdaterInteractor(object):
    def __init__(self, tp_reader, tp_updater):
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self) -> list:
        return []
