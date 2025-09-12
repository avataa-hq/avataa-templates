from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.tprm_validation.aggregate import InventoryTprmAggregate


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_bulk_update_template_parameters(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    # Assign
    template_object_id = 1
    tprm_id_1 = 141_046
    val_1 = "[8]"
    tprm_id_2 = 135_296
    val_2 = "Test"
    val_type_value_1 = "int"
    val_type_value_2 = "str"
    template_parameter_id_1 = 1
    template_parameter_id_2 = 2
    tp_1 = TemplateParameterAggregate(
        id=template_parameter_id_1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id_1),
        value=val_1,
        required=False,
        val_type=val_type_value_1,
        valid=True,
        constraint="",
    )
    tp_2 = TemplateParameterAggregate(
        id=template_parameter_id_2,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id_2),
        value=val_2,
        required=True,
        val_type=val_type_value_2,
        valid=True,
        constraint="",
    )
    mock_factory.template_parameter_reader_mock.get_by_ids.return_value = [
        tp_1,
        tp_2,
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
    request = {
        "template_object_id": template_object_id,
        "parameters": [
            {
                "id": template_parameter_id_1,
                "parameter_type_id": tprm_id_1,
                "value": val_1,
                "required": False,
            },
            {
                "id": template_parameter_id_2,
                "parameter_type_id": tprm_id_2,
                "value": val_2,
                "required": True,
            },
        ],
    }
    response = [
        {
            "id": template_parameter_id_1,
            "parameter_type_id": tprm_id_1,
            "value": val_1,
            "constraint": None,
            "required": False,
            "val_type": val_type_value_1,
            "valid": True,
        },
        {
            "id": template_parameter_id_2,
            "parameter_type_id": tprm_id_2,
            "value": val_2,
            "constraint": None,
            "required": True,
            "val_type": val_type_value_2,
            "valid": True,
        },
    ]

    # Act
    result = await http_client.post(base_url, json=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response
