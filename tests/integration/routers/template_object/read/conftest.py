from unittest.mock import AsyncMock

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.read.interactors import (
    TemplateObjectByIdReaderInteractor,
    TemplateObjectByObjectTypeReaderInteractor,
    TemplateObjectReaderInteractor,
)
from config import setup_config
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.query import TemplateParameterReader
from presentation.security.security_factory import security


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)
    from presentation.api.v1.endpoints.template_object_router import router

    _app.include_router(router)
    return _app


class MockFactory:
    def __init__(self):
        self.to_reader_mock = AsyncMock(spec=TemplateObjectReader)
        self.tp_reader_mock = AsyncMock(spec=TemplateParameterReader)


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
    def get_template_object_reader_repo(
        self, session: AsyncSession
    ) -> TemplateObjectReader:
        return self.mock_factory.to_reader_mock

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_reader_repo(
        self, session: AsyncSession
    ) -> TemplateParameterReader:
        return self.mock_factory.tp_reader_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_template_object_reader(
        self, to_repo: TemplateObjectReader, tp_repo: TemplateParameterReader
    ) -> TemplateObjectReaderInteractor:
        return TemplateObjectReaderInteractor(to_repo=to_repo, tp_repo=tp_repo)

    @provide(scope=Scope.REQUEST)
    def get_template_object_by_id_reader(
        self, to_repo: TemplateObjectReader, tp_repo: TemplateParameterReader
    ) -> TemplateObjectByIdReaderInteractor:
        return TemplateObjectByIdReaderInteractor(
            to_repo=to_repo, tp_repo=tp_repo
        )

    @provide(scope=Scope.REQUEST)
    def get_template_object_by_object_id_reader(
        self, to_repo: TemplateObjectReader
    ) -> TemplateObjectByObjectTypeReaderInteractor:
        return TemplateObjectByObjectTypeReaderInteractor(to_repo=to_repo)


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
    app.dependency_overrides[security] = lambda: True
    setup_dishka(container, app)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
