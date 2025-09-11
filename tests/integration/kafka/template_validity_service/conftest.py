from unittest.mock import AsyncMock

from dishka import Provider, Scope, make_async_container, provide
import pytest_asyncio

from application.common.uow import SQLAlchemyUoW
from domain.template.command import TemplateUpdater
from domain.template.query import TemplateReader
from domain.template_object.command import TemplateObjectUpdater
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import TemplateParameterUpdater
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.service import TemplateValidityService


class MockFactory:
    def __init__(self):
        self.t_reader_mock = AsyncMock(TemplateReader)
        self.t_updater_mock = AsyncMock(spec=TemplateUpdater)
        self.tp_reader_mock = AsyncMock(spec=TemplateParameterReader)
        self.tp_updater_mock = AsyncMock(spec=TemplateParameterUpdater)
        self.to_reader_mock = AsyncMock(spec=TemplateObjectReader)
        self.to_updater_mock = AsyncMock(spec=TemplateObjectUpdater)
        self.uow_mock = AsyncMock(spec=SQLAlchemyUoW)


class MockDatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_uow(self) -> SQLAlchemyUoW:
        return AsyncMock(spec=SQLAlchemyUoW)


class MockServiceProvider(Provider):
    def __init__(self, mock_factory: MockFactory):
        super().__init__()
        self.mock_factory = mock_factory

    @provide(scope=Scope.REQUEST)
    def get_template_reader_repo(self) -> TemplateReader:
        return self.mock_factory.t_reader_mock

    @provide(scope=Scope.REQUEST)
    async def get_template_updater_repo(self) -> TemplateUpdater:
        return self.mock_factory.t_updater_mock

    @provide(scope=Scope.REQUEST)
    async def get_template_parameter_reader_repo(
        self,
    ) -> TemplateParameterReader:
        return self.mock_factory.tp_reader_mock

    @provide(scope=Scope.REQUEST)
    async def get_template_parameter_updater_repos(
        self,
    ) -> TemplateParameterUpdater:
        return self.mock_factory.tp_updater_mock

    @provide(scope=Scope.REQUEST)
    async def get_template_object_reader_repo(self) -> TemplateObjectReader:
        return self.mock_factory.to_reader_mock

    @provide(scope=Scope.REQUEST)
    async def get_template_object_updater_repo(self) -> TemplateObjectUpdater:
        return self.mock_factory.to_updater_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_template_validity_service(
        self,
        t_reader: TemplateReader,
        t_updater: TemplateUpdater,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        to_reader: TemplateObjectReader,
        to_updater: TemplateObjectUpdater,
        uow: SQLAlchemyUoW,
    ) -> TemplateValidityService:
        return TemplateValidityService(
            t_reader=t_reader,
            t_updater=t_updater,
            tp_reader=tp_reader,
            tp_updater=tp_updater,
            to_reader=to_reader,
            to_updater=to_updater,
            uow=uow,
        )


@pytest_asyncio.fixture
def mock_factory():
    return MockFactory()


@pytest_asyncio.fixture
async def container(mock_factory):
    container = make_async_container(
        MockDatabaseProvider(),
        MockServiceProvider(mock_factory),
        MockInteractorProvider(),
    )
    yield container
    await container.close()
