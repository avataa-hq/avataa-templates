from typing import AsyncIterator
from unittest.mock import AsyncMock, Mock, patch

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from config import setup_config
from di import get_async_session


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


class MockFactory:
    def __init__(self):
        pass


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


@pytest_asyncio.fixture
def mock_factory():
    return MockFactory()


@pytest_asyncio.fixture
async def container(mock_factory):
    container = make_async_container()
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
