import datetime
from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import UoW
from config import setup_config
from models import TemplateObject, TemplateParameter


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
def mock_grpc_function():
    mock = AsyncMock()
    mock.return_value = [
        {
            "constraint": None,
            "modified_by": "",
            "prm_link_filter": None,
            "creation_date": datetime.datetime(2024, 10, 7, 12, 4, 10, 448541),
            "description": None,
            "group": None,
            "modification_date": datetime.datetime(
                2024, 10, 7, 14, 21, 19, 472005
            ),
            "name": "Professor's name",
            "field_value": None,
            "backward_link": None,
            "val_type": "str",
            "id": 135296,
            "tmo_id": 46181,
            "multiple": False,
            "version": 2,
            "required": True,
            "created_by": "",
            "returnable": False,
        },
        {
            "constraint": "46182",
            "modified_by": "",
            "prm_link_filter": None,
            "creation_date": datetime.datetime(2024, 10, 7, 12, 7, 13, 357795),
            "description": None,
            "group": None,
            "modification_date": datetime.datetime(
                2024, 10, 7, 12, 7, 13, 357799
            ),
            "name": "Courses",
            "field_value": None,
            "backward_link": None,
            "val_type": "mo_link",
            "id": 135297,
            "tmo_id": 46181,
            "multiple": True,
            "version": 1,
            "required": False,
            "created_by": "",
            "returnable": False,
        },
        {
            "constraint": None,
            "modified_by": "",
            "prm_link_filter": None,
            "creation_date": datetime.datetime(2024, 10, 7, 12, 10, 16, 274405),
            "description": None,
            "group": None,
            "modification_date": datetime.datetime(
                2024, 10, 7, 12, 10, 16, 274409
            ),
            "name": "Year of commencement of teaching",
            "field_value": None,
            "backward_link": None,
            "val_type": "int",
            "id": 135298,
            "tmo_id": 46181,
            "multiple": False,
            "version": 1,
            "required": False,
            "created_by": "",
            "returnable": False,
        },
        {
            "constraint": None,
            "modified_by": "",
            "prm_link_filter": None,
            "creation_date": datetime.datetime(2024, 10, 7, 12, 10, 40, 952324),
            "description": None,
            "group": None,
            "modification_date": datetime.datetime(
                2024, 10, 7, 12, 10, 40, 952326
            ),
            "name": "Year of birth",
            "field_value": None,
            "backward_link": None,
            "val_type": "str",
            "id": 135299,
            "tmo_id": 46181,
            "multiple": False,
            "version": 1,
            "required": False,
            "created_by": "",
            "returnable": False,
        },
    ]
    return mock


@pytest.fixture
def mock_db():
    id_counter = 1

    def mock_add(obj: TemplateParameter):
        nonlocal id_counter
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = id_counter
            id_counter += 1
        for field, value in obj.__table__.columns.items():
            if getattr(obj, field) is None:
                setattr(obj, field, "null")

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

    db.add = Mock(side_effect=mock_add)
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    return db


# @pytest.fixture
# def mock_auth():
#     mock_user_data = MagicMock()
#     mock_user_data.user_id = "test_user_id"
#     mock_user_data.username = "test_user"
#
#     return AsyncMock(return_value=mock_user_data)


@pytest.fixture
async def http_client(app, mock_db, mock_grpc_function):
    app.dependency_overrides[UoW] = lambda: mock_db
    app.dependency_overrides[AsyncSession] = lambda: mock_db
    # app.dependency_overrides[oauth2_scheme] = lambda: mock_auth
    with patch(
        "services.template_registry_services.get_all_tprms_for_special_tmo_id_channel_in",
        mock_grpc_function,
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
    app.dependency_overrides.clear()
