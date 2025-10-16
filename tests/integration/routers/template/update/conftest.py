from typing import AsyncIterator
from unittest.mock import AsyncMock, Mock, patch

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import SQLAlchemyUoW
from application.template.update.interactors import TemplateUpdaterInteractor
from application.tmo_validation.interactors import TMOValidationInteractor
from config import setup_config
from di import get_async_session
from domain.template.command import TemplateUpdater
from domain.template.query import TemplateReader
from domain.tmo_validation.query import TMOReader
from presentation.security.security_factory import security


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)

    from presentation.api.v1.endpoints.template_router import router

    _app.include_router(router)

    return _app


# @pytest.fixture
# def mock_auth():
#     mock_user_data = MagicMock()
#     mock_user_data.user_id = "test_user_id"
#     mock_user_data.username = "test_user"
#
#     return AsyncMock(return_value=mock_user_data)


@pytest.fixture
def mock_db():
    db = AsyncMock(spec=AsyncSession)
    execute_mock = AsyncMock()
    result_mock = Mock()
    execute_mock.return_value = result_mock
    db.execute = execute_mock
    return db


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def mock_grpc_response() -> AsyncIterator:
    with (
        patch(
            "services.template_registry_services.get_all_tmo_data_from_inventory_channel_in"
        ) as get_all_tmo_data_from_inventory,
    ):
        yield get_all_tmo_data_from_inventory


class MockFactory:
    def __init__(self):
        self.inventory_tmo_validator_mock = AsyncMock(spec=TMOReader)
        self.template_reader_mock = AsyncMock(spec=TemplateReader)
        self.template_updater_mock = AsyncMock(spec=TemplateUpdater)


class MockDatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> AsyncSession:
        connection = AsyncMock(spec=AsyncSession)
        return connection

    @provide(scope=Scope.REQUEST)
    def get_uow(self, session: AsyncSession) -> SQLAlchemyUoW:
        uow = AsyncMock(spec=SQLAlchemyUoW)
        return uow


class MockRepositoryProvider(Provider):
    def __init__(self, mock_factory: MockFactory):
        super().__init__()
        self.mock_factory = mock_factory

    @provide(scope=Scope.REQUEST)
    def get_tmo_inventory_repo(self) -> TMOReader:
        return self.mock_factory.inventory_tmo_validator_mock

    @provide(scope=Scope.REQUEST)
    def get_template_reader_repo(self) -> TemplateReader:
        return self.mock_factory.template_reader_mock

    @provide(scope=Scope.REQUEST)
    def get_template_updater_repo(self) -> TemplateUpdater:
        return self.mock_factory.template_updater_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_tmo_validator(
        self, grpc_repo: TMOReader
    ) -> TMOValidationInteractor:
        return TMOValidationInteractor(grpc_repo)

    @provide(scope=Scope.REQUEST)
    def get_template_updater(
        self,
        tmo_validator: TMOValidationInteractor,
        t_reader: TemplateReader,
        t_updater: TemplateUpdater,
        uow: SQLAlchemyUoW,
    ) -> TemplateUpdaterInteractor:
        return TemplateUpdaterInteractor(
            tmo_validator=tmo_validator,
            t_reader=t_reader,
            t_updater=t_updater,
            uow=uow,
        )


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
async def http_client(app, container, mock_db, mock_grpc_response):
    # app.dependency_overrides[oauth2_scheme] = lambda: mock_auth
    app.dependency_overrides[get_async_session] = lambda: mock_db
    app.dependency_overrides[security] = lambda: True
    setup_dishka(container, app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
