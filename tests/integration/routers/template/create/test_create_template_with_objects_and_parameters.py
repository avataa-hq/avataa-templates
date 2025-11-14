from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/registry-template"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_with_objects_with_parameters(
    http_client: AsyncClient,
    base_url: str,
    mock_db,
):
    status_code = 200
    t_id = to_id = tp_id = 1

    template_object_type_id = 1
    name = "template_1"
    owner = "Adm1n"
    template_object_object_type_id = 2
    required = False
    tprm_required = True
    tprm_id = 1
    tprm_value = tprm_constraint = "Value 1"

    request = {
        "name": name,
        "owner": owner,
        "object_type_id": template_object_type_id,
        "template_objects": [
            {
                "object_type_id": template_object_object_type_id,
                "required": required,
                "parameters": [
                    {
                        "parameter_type_id": tprm_id,
                        "value": tprm_value,
                        "constraint": tprm_constraint,
                        "required": tprm_required,
                    },
                ],
            },
        ],
    }
    result = await http_client.post(base_url, json=request)
    print(result.json())
    assert result.status_code == status_code
    assert result.json()["name"] == name
    assert result.json()["owner"] == owner
    assert result.json()["object_type_id"] == template_object_type_id
    assert result.json()["id"] == t_id
    assert result.json()["valid"]
    assert result.json()["template_objects"][0]["id"] == to_id
    assert (
        result.json()["template_objects"][0]["object_type_id"]
        == template_object_object_type_id
    )
    assert result.json()["template_objects"][0]["required"] == required
    assert result.json()["template_objects"][0]["valid"]
    assert result.json()["template_objects"][0]["parameters"][0]["id"] == tp_id
    assert (
        result.json()["template_objects"][0]["parameters"][0]["value"]
        == tprm_value
    )
    assert (
        result.json()["template_objects"][0]["parameters"][0]["constraint"]
        == tprm_constraint
    )
    assert (
        result.json()["template_objects"][0]["parameters"][0]["required"]
        == tprm_required
    )
    assert (
        result.json()["template_objects"][0]["parameters"][0][
            "parameter_type_id"
        ]
        == tprm_id
    )
    assert (
        result.json()["template_objects"][0]["parameters"][0]["val_type"]
        == "str"
    )
    assert result.json()["template_objects"][0]["parameters"][0]["valid"]
