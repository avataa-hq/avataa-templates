from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.template.aggregate import TemplateAggregate
from domain.tmo_validation.aggregate import InventoryTMOAggregate
from models import Template


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/templates"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template(
    http_client: AsyncClient, base_url: str, mock_db, mock_factory
) -> None:
    # Assign
    template_id = 1
    tmo_id = 1
    name_before = "Template Name A"
    name_after = "Template Name X"
    owner_before = "Owner"
    owner_after = "Updated Owner"
    full_url = f"{base_url}/{template_id}"
    request = {
        "name": name_after,
        "owner": owner_after,
        "object_type_id": tmo_id,
    }
    cr_date = datetime.now(tz=timezone.utc)
    mod_date = datetime.now(tz=timezone.utc) + timedelta(seconds=1)
    t = Template(
        name=name_before,
        owner=owner_before,
        object_type_id=tmo_id,
        creation_date=cr_date,
        modification_date=cr_date,
        valid=True,
        version=1,
    )
    t.id = template_id
    mock_db.execute.return_value.scalar_one_or_none.return_value = t
    t_aggr = TemplateAggregate(
        id=TemplateId(template_id),
        name=name_before,
        owner=owner_before,
        object_type_id=ObjectTypeId(tmo_id),
        creation_date=cr_date,
        modification_date=cr_date,
        valid=True,
        version=1,
    )
    t_aggr_new = TemplateAggregate(
        id=TemplateId(template_id),
        name=name_after,
        owner=owner_after,
        object_type_id=ObjectTypeId(tmo_id),
        creation_date=cr_date,
        modification_date=mod_date,
        valid=True,
        version=2,
    )

    mock_factory.template_reader_mock.get_by_id.return_value = t_aggr
    mock_factory.template_updater_mock.update_template.return_value = t_aggr_new
    response = {
        "id": template_id,
        "name": name_after,
        "object_type_id": tmo_id,
        "owner": owner_after,
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
    base_url: str,
    mock_db,
    mock_factory,
    mock_grpc_response,
) -> None:
    # Assign
    template_id = 1
    tmo_id_old = 1
    tmo_id_new = 2
    name_before = "Template Name A"
    name_after = "Template Name X"
    owner_before = "Owner"
    owner_after = "Updated Owner"
    grpc_response = [
        InventoryTMOAggregate(id=tmo_id_old, parent_id=None),
        InventoryTMOAggregate(id=tmo_id_new, parent_id=None),
    ]
    get_all_tmo_data_from_inventory = mock_grpc_response
    get_all_tmo_data_from_inventory.return_value = grpc_response

    full_url = f"{base_url}/{template_id}"
    request = {
        "name": name_after,
        "owner": owner_after,
        "object_type_id": tmo_id_new,
    }
    cr_date = datetime.now(tz=timezone.utc)
    mod_date = datetime.now(tz=timezone.utc) + timedelta(seconds=1)
    t = Template(
        name=name_before,
        owner=owner_before,
        object_type_id=tmo_id_old,
        creation_date=cr_date,
        modification_date=cr_date,
        valid=True,
        version=1,
    )
    t.id = template_id
    mock_db.execute.return_value.scalar_one_or_none.return_value = t
    response = {
        "id": template_id,
        "name": name_after,
        "object_type_id": tmo_id_new,
        "owner": "Updated Owner",
        "valid": True,
    }
    t_aggr = TemplateAggregate(
        id=TemplateId(template_id),
        name=name_before,
        owner=owner_before,
        object_type_id=ObjectTypeId(tmo_id_old),
        creation_date=cr_date,
        modification_date=cr_date,
        valid=True,
        version=1,
    )
    t_aggr_new = TemplateAggregate(
        id=TemplateId(template_id),
        name=name_after,
        owner=owner_after,
        object_type_id=ObjectTypeId(tmo_id_new),
        creation_date=cr_date,
        modification_date=mod_date,
        valid=True,
        version=2,
    )

    mock_factory.template_reader_mock.get_by_id.return_value = t_aggr
    mock_factory.template_updater_mock.update_template.return_value = t_aggr_new
    mock_factory.inventory_tmo_validator_mock.get_all_tmo_data.return_value = (
        grpc_response
    )
    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_with_change_tmo_id_error(
    http_client: AsyncClient,
    base_url: str,
    mock_db,
    mock_factory,
    mock_grpc_response,
) -> None:
    # Assert
    template_id = 1
    tmo_id_old = 1
    tmo_id_new = 2
    name_before = "Template Name A"
    name_after = "Template Name X"
    owner_before = "Owner"
    owner_after = "Updated Owner"
    grpc_response = [
        InventoryTMOAggregate(id=tmo_id_old, parent_id=None),
        InventoryTMOAggregate(id=tmo_id_new + 1, parent_id=None),
    ]
    get_all_tmo_data_from_inventory = mock_grpc_response
    get_all_tmo_data_from_inventory.return_value = grpc_response

    full_url = f"{base_url}/{template_id}"
    request = {
        "name": name_after,
        "owner": owner_after,
        "object_type_id": tmo_id_new,
    }
    date = datetime.now(tz=timezone.utc)
    t = Template(
        name=name_before,
        owner=owner_before,
        object_type_id=tmo_id_old,
        creation_date=date,
        modification_date=date,
        valid=True,
        version=1,
    )
    t.id = 1
    mock_db.execute.return_value.scalar_one_or_none.return_value = t
    t_aggr = TemplateAggregate(
        id=TemplateId(1),
        name=name_before,
        owner=owner_before,
        object_type_id=ObjectTypeId(tmo_id_old),
        creation_date=date,
        modification_date=date,
        valid=True,
        version=1,
    )
    mock_factory.template_reader_mock.get_by_id.return_value = t_aggr
    mock_factory.inventory_tmo_validator_mock.get_all_tmo_data.return_value = (
        grpc_response
    )
    response = {"detail": f"TMO id {tmo_id_new} not found in inventory."}
    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == 404
    assert result.json() == response
