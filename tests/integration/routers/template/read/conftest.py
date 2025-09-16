from unittest.mock import AsyncMock

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from application.template.read.interactors import TemplateReaderInteractor
from config import setup_config
from domain.template.query import TemplateReader


@pytest.fixture
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)
    from presentation.api.v1.endpoints.template_router import router

    _app.include_router(router)
    return _app


class MockFactory:
    def __init__(self):
        self.template_reader_mock = AsyncMock(spec=TemplateReader)


class MockDatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> AsyncSession:
        connection = AsyncMock(spec=AsyncSession)
        return connection


class MockRepositoryProvider(Provider):
    def __init__(self, mock_factory: MockFactory):
        super().__init__()
        self.mock_factory = mock_factory

    @provide(scope=Scope.REQUEST)
    async def get_template_reader_repo(
        self, session: AsyncSession
    ) -> TemplateReader:
        return self.mock_factory.template_reader_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_template_reader(
        self, repo: TemplateReader
    ) -> TemplateReaderInteractor:
        return TemplateReaderInteractor(t_repo=repo)


@pytest_asyncio.fixture
def mock_factory():
    return MockFactory()


@pytest_asyncio.fixture
async def container(mock_factory):
    container = make_async_container(
        MockDatabaseProvider(),
        MockRepositoryProvider(mock_factory),
        MockInteractorProvider(),
    )
    yield container
    await container.close()


@pytest.fixture
async def http_client(app, container):
    # app.dependency_overrides[oauth2_scheme] = lambda: mock_auth
    setup_dishka(container, app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
