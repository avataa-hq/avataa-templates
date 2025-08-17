from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import UoW
from application.template_object.read.interactors import (
    TemplateObjectReaderInteractor,
)
from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId


@pytest.fixture
# def app(mock_auth):
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)

    from di import init_dependencies

    init_dependencies(_app)

    from presentation.api.v1.endpoints.template_object_router import router

    _app.include_router(router)

    return _app


@pytest.fixture
def mock_db():
    fake_client = AsyncMock()
    return fake_client


@pytest.fixture
def fake_tp_repo() -> AsyncMock:
    repo = AsyncMock(spec=TemplateParameterReader)
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_296),
        value="Value 1",
        constraint="Value 1",
        val_type="str",
        required=True,
        valid=True,
    )
    param_2 = TemplateParameterAggregate(
        id=2,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_297),
        value="[1, 2]",
        constraint=None,
        val_type="mo_link",
        required=False,
        valid=True,
    )
    param_3 = TemplateParameterAggregate(
        id=3,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_298),
        value="1234567",
        constraint=None,
        val_type="int",
        required=False,
        valid=True,
    )
    param_4 = TemplateParameterAggregate(
        id=4,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_299),
        value="123",
        constraint=None,
        val_type="str",
        required=True,
        valid=True,
    )
    repo.get_by_filter.return_value = [param_1, param_2, param_3, param_4]
    return repo


@pytest.fixture
def fake_to_repo() -> AsyncMock:
    repo = AsyncMock(spec=TemplateObjectReader)
    obj_1 = TemplateObjectAggregate(
        id=TemplateObjectId(1),
        template_id=TemplateId(1),
        parent_object_id=None,
        object_type_id=ObjectTypeId(46181),
        required=True,
        valid=True,
    )
    repo.get_by_filter.return_value = [obj_1]
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
    app.dependency_overrides[UoW] = lambda: mock_db
    app.dependency_overrides[AsyncSession] = lambda: mock_db
    app.dependency_overrides[TemplateObjectReader] = lambda: fake_to_repo
    app.dependency_overrides[TemplateParameterReader] = lambda: fake_tp_repo
    app.dependency_overrides[TemplateObjectReaderInteractor] = (
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
