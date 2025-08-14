from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import UoW
from config import setup_config
from models import TemplateObject


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)

    from di import init_dependencies

    init_dependencies(_app)

    from presentation.api.v1.endpoints.template_registry_router import router

    _app.include_router(router)

    return _app


@pytest.fixture
def mock_grpc():
    stub_mock = AsyncMock()

    fake_chunk = AsyncMock()
    fake_chunk.tprms_data = [
        "800363680000000000000000000000000000000000000000".encode().hex()
    ]

    async def fake_grpc_stream(_):
        yield fake_chunk

    stub_mock.GetAllTPRMSByTMOId.side_effect = fake_grpc_stream

    return stub_mock


@pytest.fixture
def mock_db(mock_grpc):
    execute_mock = AsyncMock()

    result_mock = Mock()
    templ_obj = TemplateObject(
        template_id=1,
        parent_object_id=None,
        object_type_id=46181,
        required=True,
        valid=True,
    )
    templ_obj.id = 1
    result_mock.scalar_one_or_none.return_value = templ_obj

    execute_mock.return_value = result_mock
    db = AsyncMock()
    db.execute = execute_mock

    return db


# @pytest.fixture
# def mock_auth():
#     mock_user_data = MagicMock()
#     mock_user_data.user_id = "test_user_id"
#     mock_user_data.username = "test_user"
#
#     return AsyncMock(return_value=mock_user_data)


@pytest.fixture
async def http_client(app, mock_db):
    app.dependency_overrides[UoW] = lambda: mock_db
    app.dependency_overrides[AsyncSession] = lambda: mock_db
    # app.dependency_overrides[oauth2_scheme] = lambda: mock_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
