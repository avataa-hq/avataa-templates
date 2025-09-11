from unittest.mock import AsyncMock

from dishka import Provider, Scope, make_async_container, provide
import pytest_asyncio

from application.common.uow import SQLAlchemyUoW
from application.inventory_changes.interactors import InventoryChangesInteractor
from domain.template_parameter.service import TemplateParameterValidityService
from services.inventory_services.db_services import (
    TemplateObjectService,
    TemplateParameterService,
)


class MockFactory:
    def __init__(self):
        self.to_service_mock = AsyncMock(spec=TemplateObjectService)
        self.tp_service_mock = AsyncMock(spec=TemplateParameterService)
        self.tp_validity_service_mock = AsyncMock(
            spec=TemplateParameterValidityService
        )
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
    async def get_to_service(self) -> TemplateObjectService:
        return self.mock_factory.to_service_mock

    @provide(scope=Scope.REQUEST)
    async def get_tp_service(self) -> TemplateParameterService:
        return self.mock_factory.tp_service_mock

    @provide(scope=Scope.REQUEST)
    async def get_tp_validity_service(self) -> TemplateParameterValidityService:
        return self.mock_factory.tp_validity_service_mock


class MockInteractorProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_inventory_interactor(
        self,
        to_service: TemplateObjectService,
        tp_service: TemplateParameterService,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> InventoryChangesInteractor:
        return InventoryChangesInteractor(
            to_service=to_service,
            tp_service=tp_service,
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
        MockServiceProvider(mock_factory),
        MockInteractorProvider(),
    )
    yield container
    await container.close()
