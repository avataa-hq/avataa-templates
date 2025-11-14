from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/registry-template"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_with_objects(
    http_client: AsyncClient,
    base_url: str,
    mock_db,
):
    # {
    #     "name": "Template Name",
    #     "owner": "Admin",
    #     "object_type_id": 1,
    #     "template_objects": [
    #         {
    #             "object_type_id": 46181,
    #             "required": true,
    #             "parameters": [
    #                 {
    #                     "parameter_type_id": 135296,
    #                     "value": "Value 1",
    #                     "constraint": "Value 1",
    #                     "required": true,
    #                 },
    #                 {"parameter_type_id": 135297, "value": "[1, 2]", "required": false},
    #                 {
    #                     "parameter_type_id": 135298,
    #                     "value": "1234567",
    #                     "required": false,
    #                 },
    #             ],
    #         }
    #     ],
    # }
    status_code = 200
    t_id = to_id = 1

    template_object_type_id = 1
    name = "template_1"
    owner = "Adm1n"
    template_object_object_type_id = 2
    required = False

    request = {
        "name": name,
        "owner": owner,
        "object_type_id": template_object_type_id,
        "template_objects": [
            {
                "object_type_id": template_object_object_type_id,
                "required": required,
            },
        ],
    }
    result = await http_client.post(base_url, json=request)

    assert result.status_code == status_code
    assert result.json()["name"] == name
    assert result.json()["owner"] == owner
    assert result.json()["object_type_id"] == template_object_type_id
    assert result.json()["id"] == t_id
    assert result.json()["template_objects"][0]["id"] == to_id
    assert (
        result.json()["template_objects"][0]["object_type_id"]
        == template_object_object_type_id
    )
    assert result.json()["template_objects"][0]["required"] == required
