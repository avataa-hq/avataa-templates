from sqlalchemy.ext.asyncio import AsyncSession

from domain.template_parameter.command import TemplateParameterCreator


class SQLTemplateParameterCreatorRepository(TemplateParameterCreator):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_template_parameter(self, create_dto) -> None:
        raise NotImplementedError()
