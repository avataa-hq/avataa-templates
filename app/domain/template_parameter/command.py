from typing import Protocol


class TemplateParameterCreator(Protocol):
    async def create_template_parameter(self, create_dto): ...
