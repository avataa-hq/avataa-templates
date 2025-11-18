import datetime
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
from models import Template
from presentation.security.security_factory import security


@pytest.fixture
def app():
    v1_prefix = f"{setup_config().app.prefix}/v{setup_config().app.app_version}"
    _app = FastAPI(root_path=v1_prefix)

    from presentation.api.v1.endpoints.template_registry_router import router

    _app.include_router(router)

    return _app


class MockFactory:
    def __init__(self):
        pass


@pytest.fixture
def mock_db():
    db = AsyncMock(spec=AsyncSession)
    execute_mock = AsyncMock()
    first_result = Mock()
    first_result.refresh.return_value = {
        "id": 1,
        "template_id": 1,
        "parent_object_id": None,
        "object_type_id": 46181,
        "required": True,
        "valid": True,
    }
    execute_mock.return_value = first_result
    db.execute = execute_mock
    return db


@pytest_asyncio.fixture
def mock_factory():
    return MockFactory()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def mock_grpc_tmo():
    mock = AsyncMock()
    mock.return_value = [
        {
            "created_by": "Adm1n",
            "creation_date": "2025-08-11T09:43:55.183405",
            "description": None,
            "geometry_type": None,
            "global_uniqueness": False,
            "icon": None,
            "id": 1,
            "inherit_location": False,
            "label": [],
            "latitude": None,
            "lifecycle_process_definition": None,
            "line_type": None,
            "longitude": None,
            "materialize": True,
            "minimize": False,
            "modification_date": "2025-08-11T09:43:55.183417",
            "modified_by": "Adm1n",
            "name": "TestTMO",
            "p_id": None,
            "points_constraint_by_tmo": [],
            "primary": [],
            "severity_id": None,
            "status": None,
            "version": 1,
            "virtual": False,
        },
        {
            "created_by": "Adm1n",
            "creation_date": "2025-11-12T14:19:28.804670",
            "description": "Asset TMO",
            "geometry_type": None,
            "global_uniqueness": False,
            "icon": None,
            "id": 2,
            "inherit_location": False,
            "label": [479],
            "latitude": None,
            "lifecycle_process_definition": "Process_1dpt6jd:1",
            "line_type": None,
            "longitude": None,
            "materialize": True,
            "minimize": False,
            "modification_date": "2025-11-12T14:19:29.680964",
            "modified_by": "Adm1n",
            "name": "Asset",
            "p_id": 272,
            "points_constraint_by_tmo": [],
            "primary": [481],
            "severity_id": 477,
            "status": 483,
            "version": 2,
            "virtual": False,
        },
    ]
    return mock


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def mock_grpc_tprm():
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
            "id": 1,
            "tmo_id": 2,
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
            "id": 2,
            "tmo_id": 2,
            "multiple": True,
            "version": 1,
            "required": False,
            "created_by": "",
            "returnable": False,
        },
    ]
    return mock


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def mock_grpc_response(mock_grpc_tmo, mock_grpc_tprm) -> AsyncIterator:
    with (
        patch(
            "services.template_registry_services.get_all_tmo_data_from_inventory_channel_in",
            mock_grpc_tmo,
        ) as get_all_tmo_data_from_inventory,
        patch(
            "services.template_registry_services.get_all_tprms_for_special_tmo_id_channel_in",
            mock_grpc_tprm,
        ) as get_all_tprms_for_special_tmo_id,
    ):
        yield (
            get_all_tmo_data_from_inventory,
            get_all_tprms_for_special_tmo_id,
        )


@pytest_asyncio.fixture
async def container(mock_factory):
    container = make_async_container()
    yield container
    await container.close()


@pytest_asyncio.fixture
async def mock_template(test_session):
    template = Template(
        name="Template1", owner="Admin", object_type_id=1, valid=True
    )
    test_session.add(template)
    await test_session.commit()
    yield
    test_session.delete(template)
    await test_session.commit()


@pytest.fixture
async def http_client(
    app, container, test_session, mock_grpc_response, mock_template
):
    app.dependency_overrides[get_async_session] = lambda: test_session
    app.dependency_overrides[security] = lambda: True
    setup_dishka(container, app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
