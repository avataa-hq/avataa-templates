from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/add-parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter(http_client: AsyncClient, url: str):
    template_object_id = 1
    full_url = f"{url}/{template_object_id}/"
    request = [{"parameter_type_id": 135299, "value": "123", "required": True}]
    response = [
        {
            "id": 1,
            "parameter_type_id": 135299,
            "value": "123",
            "constraint": None,
            "required": True,
            "val_type": "str",
            "valid": True,
        }
    ]
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response
