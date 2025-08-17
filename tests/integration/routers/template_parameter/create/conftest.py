import datetime
from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import UoW
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
from config import setup_config
from domain.inventory_tprm.aggregate import InventoryTprmAggregate
from domain.inventory_tprm.query import TPRMReader
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.command import TemplateParameterCreator
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
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
    repo.get_object_type_by_id.return_value = obj_1.object_type_id.to_raw()
    return repo


@pytest.fixture
def fake_tp_repo() -> AsyncMock:
    repo = AsyncMock(spec=TemplateParameterCreator)
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_299),
        value="123",
        required=True,
        val_type="str",
        valid=True,
        constraint=None,
    )

    repo.create_template_parameters.return_value = [param_1]
    return repo


@pytest.fixture
def mock_grpc_new():
    repo = AsyncMock(spec=TPRMReader)
    repo.get_all_tprms_by_tmo_id.return_value = {
        46181: {
            135296: InventoryTprmAggregate(
                val_type="str",
                required=True,
                multiple=False,
                id=135296,
                constraint=None,
            ),
            135297: InventoryTprmAggregate(
                val_type="mo_link",
                required=False,
                multiple=True,
                id=135297,
                constraint="46182",
            ),
            135298: InventoryTprmAggregate(
                val_type="int",
                required=False,
                multiple=False,
                id=135298,
                constraint=None,
            ),
            135299: InventoryTprmAggregate(
                val_type="str",
                required=False,
                multiple=False,
                id=135299,
                constraint=None,
            ),
        }
    }

    return repo


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
    templ_obj_id = TemplateObject(
        template_id=1,
        parent_object_id=None,
        object_type_id=46181,
        required=True,
        valid=True,
    )
    templ_obj_id.id = 1
    result_mock.scalar_one_or_none.return_value = templ_obj_id.object_type_id
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
async def http_client(
    app, mock_db, mock_grpc_function, mock_grpc_new, fake_to_repo, fake_tp_repo
):
    app.dependency_overrides[UoW] = lambda: mock_db
    app.dependency_overrides[AsyncSession] = lambda: mock_db
    app.dependency_overrides[TPRMReader] = lambda: mock_grpc_new
    app.dependency_overrides[TemplateParameterCreatorInteractor] = (
        lambda: TemplateParameterCreatorInteractor(
            to_repo=fake_to_repo,
            tp_repo=fake_tp_repo,
            inventory_tprm_repo=mock_grpc_new,
            uow=mock_db,
        )
    )

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
