from logging import getLogger


class TemplateParameterUpdaterInteractor(object):
    def __init__(self):
        self.logger = getLogger("TemplateParameterUpdaterInteractor")

    async def __call__(self) -> list:
        return []
