from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/add-objects"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_objects(
    http_client: AsyncClient,
    base_url: str,
    mock_db,
):
    status_code = 200
    t_id = 1
    object_type_id = 2
    value = "Value 1"
    parameter_type_id = 1

    required = False
    full_url = f"{base_url}/{t_id}"

    request = [
        {
            "object_type_id": object_type_id,
            "required": required,
            "parameters": [
                {
                    "parameter_type_id": parameter_type_id,
                    "value": value,
                    "required": True,
                }
            ],
        }
    ]
    result = await http_client.post(full_url, json=request)
    # print(result.json())
    assert result.status_code == status_code
    assert result.json()[0]["object_type_id"] == object_type_id
    assert result.json()[0]["parameters"][0]["id"] == 1
    assert result.json()[0]["parameters"][0]["value"] == value
    assert result.json()[0]["parameters"][0]["val_type"] == "str"
    assert result.json()[0]["parameters"][0]["valid"]
