from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.tprm_validation.aggregate import InventoryTprmAggregate


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/add-parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    template_object_id = 1
    tprm_id = 135_299
    val = "123"
    full_url = f"{base_url}/{template_object_id}"
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=True,
        val_type="str",
        valid=True,
        constraint=None,
    )
    mock_factory.template_parameter_reader_mock.exists.return_value = False
    mock_factory.template_parameter_creator_mock.create_template_parameters.return_value = [
        param_1
    ]

    mock_factory.template_object_reader_mock.get_object_type_by_id.return_value = 46_181
    mock_factory.inventory_tprm_validator_mock.get_all_tprms_by_tmo_id.return_value = {
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
        141046: InventoryTprmAggregate(
            val_type="int",
            required=False,
            multiple=True,
            id=141046,
            constraint=None,
        ),
        141047: InventoryTprmAggregate(
            val_type="bool",
            required=False,
            multiple=True,
            id=141047,
            constraint=None,
        ),
    }
    request = [{"parameter_type_id": tprm_id, "value": val, "required": True}]
    response = [
        {
            "id": 1,
            "parameter_type_id": tprm_id,
            "value": val,
            "constraint": None,
            "required": True,
            "val_type": "str",
            "valid": True,
        }
    ]
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("val", ["[False, True]", "[false, true]"])
async def test_create_template_parameter_multiple_bool(
    http_client: AsyncClient,
    base_url: str,
    val: str,
    mock_factory,
):
    template_object_id = 1
    full_url = f"{base_url}/{template_object_id}"
    tprm_id = 141_047
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=False,
        val_type="bool",
        valid=True,
        constraint=None,
    )
    mock_factory.inventory_tprm_validator_mock.get_all_tprms_by_tmo_id.return_value = {
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
        141046: InventoryTprmAggregate(
            val_type="int",
            required=False,
            multiple=True,
            id=141046,
            constraint=None,
        ),
        141047: InventoryTprmAggregate(
            val_type="bool",
            required=False,
            multiple=True,
            id=141047,
            constraint=None,
        ),
    }
    mock_factory.template_parameter_reader_mock.exists.return_value = False
    mock_factory.template_parameter_creator_mock.create_template_parameters.return_value = [
        param_1
    ]
    mock_factory.template_object_reader_mock.get_object_type_by_id.return_value = 46_181

    request = [{"parameter_type_id": tprm_id, "value": val, "required": False}]
    response = [
        {
            "id": 1,
            "parameter_type_id": tprm_id,
            "value": val,
            "constraint": None,
            "required": False,
            "val_type": "bool",
            "valid": True,
        }
    ]
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter_with_already_exists_parameter(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    template_object_id = 1
    tprm_id = 135_299
    val = "123"
    full_url = f"{base_url}/{template_object_id}"
    mock_factory.template_parameter_reader_mock.exists.return_value = True

    request = [{"parameter_type_id": tprm_id, "value": val, "required": True}]
    response = {"detail": "The template parameter(s) already exist(s)."}
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 422
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter_from_incorrect_tmo(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    # Assign
    template_object_id = 1
    val = "1"
    tprm_id = 100
    inconsistent_tprm_id = tprm_id + 1
    tmo_id = 46_181
    status_code = 422
    full_url = f"{base_url}/{template_object_id}"
    detail_error = f"Inconsistent request parameters: {[inconsistent_tprm_id]} do not belong tmo {tmo_id}."

    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=False,
        val_type="bool",
        valid=True,
        constraint=None,
    )
    mock_factory.template_parameter_reader_mock.exists.return_value = False
    mock_factory.template_parameter_creator_mock.create_template_parameters.return_value = [
        param_1
    ]
    mock_factory.template_object_reader_mock.get_object_type_by_id.return_value = tmo_id
    mock_factory.inventory_tprm_validator_mock.get_all_tprms_by_tmo_id.return_value = {
        tprm_id: []
    }

    request = [
        {
            "parameter_type_id": inconsistent_tprm_id,
            "value": val,
            "required": False,
        }
    ]
    response = {"detail": detail_error}
    # Act
    result = await http_client.post(full_url, json=request)
    # Assert
    assert result.status_code == status_code
    assert result.json() == response
