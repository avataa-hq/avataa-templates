from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from application.template_object.read.interactors import (
    TemplateObjectReaderInteractor,
)
from config import setup_config
from di import (
    get_async_session,
    get_template_object_reader_repository,
    get_template_parameter_reader_repository,
    get_unit_of_work,
    read_template_object_interactor,
)
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.query import TemplateParameterReader


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)
    from presentation.api.v1.endpoints.template_object_router import router

    _app.include_router(router)
    return _app


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def fake_tp_repo() -> AsyncMock:
    repo = AsyncMock(spec=TemplateParameterReader)
    return repo


@pytest.fixture
def fake_to_repo() -> AsyncMock:
    repo = AsyncMock(spec=TemplateObjectReader)
    return repo


# @pytest.fixture
# def mock_auth():
#     mock_user_data = MagicMock()
#     mock_user_data.user_id = "test_user_id"
#     mock_user_data.username = "test_user"
#
#     return AsyncMock(return_value=mock_user_data)


@pytest.fixture
async def http_client(app, mock_db, fake_tp_repo, fake_to_repo):
    app.dependency_overrides[get_unit_of_work] = lambda: mock_db
    app.dependency_overrides[get_async_session] = lambda: mock_db
    app.dependency_overrides[get_template_object_reader_repository] = (
        lambda: fake_to_repo
    )
    app.dependency_overrides[get_template_parameter_reader_repository] = (
        lambda: fake_tp_repo
    )
    app.dependency_overrides[read_template_object_interactor] = (
        lambda: TemplateObjectReaderInteractor(
            to_repo=fake_to_repo,
            tp_repo=fake_tp_repo,
        )
    )
    # app.dependency_overrides[oauth2_scheme] = lambda: mock_auth

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
