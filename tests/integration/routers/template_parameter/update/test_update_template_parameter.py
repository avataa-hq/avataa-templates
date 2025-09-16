from httpx import AsyncClient
import pytest

from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from config import setup_config
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.tprm_validation.aggregate import InventoryTprmAggregate


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_parameter(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    # Assign
    template_parameter_id = 1
    tprm_id = 141_046
    val = "[8]"
    required_value = False
    val_type_value = "int"
    full_url = f"{base_url}/{template_parameter_id}"
    mock_factory.template_parameter_reader_mock.get_by_id.return_value = (
        TemplateParameterAggregate(
            id=1,
            template_object_id=TemplateObjectId(template_parameter_id),
            parameter_type_id=ParameterTypeId(tprm_id),
            value=val,
            required=required_value,
            val_type=val_type_value,
            valid=True,
            constraint="",
        )
    )
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
    request = {
        "parameter_type_id": tprm_id,
        "value": val,
        "required": required_value,
    }
    response = {
        "id": 1,
        "parameter_type_id": tprm_id,
        "value": val,
        "constraint": None,
        "required": required_value,
        "val_type": val_type_value,
        "valid": True,
    }

    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_incorrect_update_template_parameter(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    # Assign
    template_parameter_id = 1
    val = "[8]"
    required_value = False
    full_url = f"{base_url}/{template_parameter_id}"
    error_message = "Template Parameter not found."
    error_code = 404
    mock_factory.template_parameter_reader_mock.get_by_id.side_effect = (
        TemplateParameterReaderApplicationException(
            status_code=error_code, detail=error_message
        )
    )
    request = {
        "parameter_type_id": 18,
        "value": val,
        "required": required_value,
    }
    response = {"detail": error_message}

    # Act
    result = await http_client.put(full_url, json=request)
    # Assert
    assert result.status_code == error_code
    assert result.json() == response
    mock_factory.template_parameter_reader_mock.get_by_id.assert_called_once()
