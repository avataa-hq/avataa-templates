from logging import getLogger


class TemplateParameterValidityService:
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    async def recalculate_template_validity_after_parameter_update(self): ...
