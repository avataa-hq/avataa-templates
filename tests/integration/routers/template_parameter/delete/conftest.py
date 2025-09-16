from unittest.mock import AsyncMock, Mock

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import SQLAlchemyUoW
from application.template_parameter.delete.interactors import (
    TemplateParameterDeleterInteractor,
)
from config import setup_config
from di import get_async_session
from domain.template_parameter.command import TemplateParameterDeleter
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.service import TemplateParameterValidityService


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)

    from presentation.api.v1.endpoints.template_parameter_router import router

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


class MockFactory:
    def __init__(self):
        self.tp_deleter_mock = AsyncMock(spec=TemplateParameterDeleter)
        self.tp_reader_mock = AsyncMock(spec=TemplateParameterReader)
        self.tp_validity_service_mock = AsyncMock(
            spec=TemplateParameterValidityService
        )


@pytest_asyncio.fixture
def mock_factory():
    return MockFactory()


class MockDatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_uow(self) -> SQLAlchemyUoW:
        uow = AsyncMock(spec=SQLAlchemyUoW)
        return uow


class MockRepositoryProvider(Provider):
    def __init__(self, mock_factory: MockFactory):
        super().__init__()
        self.mock_factory = mock_factory

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_deleter_repo(self) -> TemplateParameterDeleter:
        return self.mock_factory.tp_deleter_mock

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_reader_repo(self) -> TemplateParameterReader:
        return self.mock_factory.tp_reader_mock

    @provide(scope=Scope.REQUEST)
    async def get_tp_validity_service(self) -> TemplateParameterValidityService:
        return self.mock_factory.tp_validity_service_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_template_parameter_deleter(
        self,
        tp_reader: TemplateParameterReader,
        tp_deleter: TemplateParameterDeleter,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterDeleterInteractor:
        return TemplateParameterDeleterInteractor(
            tp_deleter=tp_deleter,
            tp_reader=tp_reader,
            tp_validity_service=tp_validity_service,
            uow=uow,
        )


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
    setup_dishka(container, app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
