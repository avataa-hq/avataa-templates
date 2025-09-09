from datetime import datetime, timezone

from httpx import AsyncClient
import pytest

from config import setup_config
from models import Template


@pytest.fixture(scope="session")
def url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/templates"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template(
    http_client: AsyncClient, url: str, mock_db, mock_factory
) -> None:
    # Assign
    template_id = 1
    full_url = f"{url}/{template_id}"
    request = {
        "name": "Template Name X",
        "owner": "Updated Owner",
        "object_type_id": 1,
    }
    date = datetime.now(tz=timezone.utc)
    t = Template(
        name="Template Name A",
        owner="Owner",
        object_type_id=1,
        creation_date=date,
        modification_date=date,
        valid=True,
        version=1,
    )
    t.id = 1
    mock_db.execute.return_value.scalar_one_or_none.return_value = t
    response = {
        "id": 1,
        "name": "Template Name X",
        "object_type_id": 1,
        "owner": "Updated Owner",
        "valid": True,
    }
    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_with_change_tmo_id(
    http_client: AsyncClient,
    url: str,
    mock_db,
    mock_factory,
    mock_grpc_response,
) -> None:
    # Assign
    template_id = 1
    tmo_id_old = 1
    tmo_id_new = 2
    get_all_tmo_data_from_inventory = mock_grpc_response
    get_all_tmo_data_from_inventory.return_value = [
        {"id": tmo_id_old, "p_id": None},
        {"id": tmo_id_new, "p_id": None},
    ]

    full_url = f"{url}/{template_id}"
    request = {
        "name": "Template Name X",
        "owner": "Updated Owner",
        "object_type_id": tmo_id_new,
    }
    date = datetime.now(tz=timezone.utc)
    t = Template(
        name="Template Name A",
        owner="Owner",
        object_type_id=tmo_id_old,
        creation_date=date,
        modification_date=date,
        valid=True,
        version=1,
    )
    t.id = 1
    mock_db.execute.return_value.scalar_one_or_none.return_value = t
    response = {
        "id": 1,
        "name": "Template Name X",
        "object_type_id": tmo_id_new,
        "owner": "Updated Owner",
        "valid": True,
    }
    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_with_change_tmo_i_error(
    http_client: AsyncClient,
    url: str,
    mock_db,
    mock_factory,
    mock_grpc_response,
) -> None:
    # Assert
    template_id = 1
    tmo_id_old = 1
    tmo_id_new = 2
    get_all_tmo_data_from_inventory = mock_grpc_response
    get_all_tmo_data_from_inventory.return_value = [
        {"id": tmo_id_old, "p_id": None},
        {"id": tmo_id_new + 1, "p_id": None},
    ]

    full_url = f"{url}/{template_id}"
    request = {
        "name": "Template Name X",
        "owner": "Updated Owner",
        "object_type_id": tmo_id_new,
    }
    date = datetime.now(tz=timezone.utc)
    t = Template(
        name="Template Name A",
        owner="Owner",
        object_type_id=tmo_id_old,
        creation_date=date,
        modification_date=date,
        valid=True,
        version=1,
    )
    t.id = 1
    mock_db.execute.return_value.scalar_one_or_none.return_value = t
    response = {"detail": f"TMO id {tmo_id_new} not found in inventory."}
    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == 404
    assert result.json() == response
