from unittest.mock import AsyncMock

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from application.common.uow import SQLAlchemyUoW
from application.template_parameter.update.interactors import (
    BulkTemplateParameterUpdaterInteractor,
    TemplateParameterUpdaterInteractor,
)
from application.tprm_validation.interactors import (
    ParameterValidationInteractor,
)
from config import setup_config
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import TemplateParameterUpdater
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.service import TemplateParameterValidityService
from domain.tprm_validation.query import TPRMReader
from presentation.security.security_factory import security


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


class MockFactory:
    def __init__(self):
        self.template_object_reader_mock = AsyncMock(spec=TemplateObjectReader)
        self.template_parameter_reader_mock = AsyncMock(
            spec=TemplateParameterReader
        )
        self.template_parameter_updater_mock = AsyncMock(
            spec=TemplateParameterUpdater
        )
        self.inventory_tprm_validator_mock = AsyncMock(spec=TPRMReader)
        self.tp_validity_service_mock = AsyncMock(
            spec=TemplateParameterValidityService
        )


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
    def get_tprm_inventory_repo(self) -> TPRMReader:
        return self.mock_factory.inventory_tprm_validator_mock

    @provide(scope=Scope.REQUEST)
    def get_template_object_reader_repo(self) -> TemplateObjectReader:
        return self.mock_factory.template_object_reader_mock

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_reader_repo(self) -> TemplateParameterReader:
        return self.mock_factory.template_parameter_reader_mock

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_updater_repo(self) -> TemplateParameterUpdater:
        return self.mock_factory.template_parameter_updater_mock

    @provide(scope=Scope.REQUEST)
    async def get_tp_validity_service(self) -> TemplateParameterValidityService:
        return self.mock_factory.tp_validity_service_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_parameter_validator(
        self, grpc_repo: TPRMReader
    ) -> ParameterValidationInteractor:
        return ParameterValidationInteractor(grpc_repo)

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_updater(
        self,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterUpdaterInteractor:
        return TemplateParameterUpdaterInteractor(
            tp_reader=tp_reader,
            to_reader=to_reader,
            tp_updater=tp_updater,
            tprm_validator=tprm_validator,
            tp_validity_service=tp_validity_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_bulk_updater(
        self,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> BulkTemplateParameterUpdaterInteractor:
        return BulkTemplateParameterUpdaterInteractor(
            to_reader=to_reader,
            tp_reader=tp_reader,
            tp_updater=tp_updater,
            tprm_validator=tprm_validator,
            tp_validity_service=tp_validity_service,
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
async def http_client(app, container):
    # app.dependency_overrides[oauth2_scheme] = lambda: mock_auth
    app.dependency_overrides[security] = lambda: True
    setup_dishka(container, app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
