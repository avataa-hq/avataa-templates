from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import UoW
from config import setup_config
from models import TemplateParameter


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)

    from di import init_dependencies

    init_dependencies(_app)

    from presentation.api.v1.endpoints.template_parameter_router import router

    _app.include_router(router)

    return _app


@pytest.fixture
def mock_db():
    fake_client = AsyncMock()
    first_result = Mock()
    first_result.scalar_one_or_none.return_value = {
        "id": 1,
        "template_id": 1,
        "parent_object_id": None,
        "object_type_id": 46181,
        "required": True,
        "valid": True,
    }

    session_scalars = Mock()
    scalars_all = Mock()
    param_1 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_296,
        value="Value 1",
        constraint="Value 1",
        val_type="str",
        required=True,
        valid=True,
    )
    param_1.id = 1
    param_2 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_297,
        value="[1, 2]",
        constraint=None,
        val_type="mo_link",
        required=False,
        valid=True,
    )
    param_2.id = 2
    param_3 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_298,
        value="1234567",
        constraint=None,
        val_type="int",
        required=False,
        valid=True,
    )
    param_3.id = 3

    scalars_all.all.return_value = [param_1, param_2, param_3]
    session_scalars.scalars.return_value = scalars_all
    fake_client.execute.side_effect = [first_result, session_scalars]
    fake_client.scalars.return_value = scalars_all

    return fake_client


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
