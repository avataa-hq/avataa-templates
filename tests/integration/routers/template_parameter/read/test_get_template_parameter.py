from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_search_template_parameter(http_client: AsyncClient, url: str):
    request = {"template_object_id": "1"}
    response = [
        {
            "id": 1,
            "parameter_type_id": 135_296,
            "value": "Value 1",
            "constraint": "Value 1",
            "val_type": "str",
            "required": True,
            "valid": True,
        },
        {
            "id": 2,
            "parameter_type_id": 135_297,
            "value": "[1, 2]",
            "constraint": None,
            "val_type": "mo_link",
            "required": False,
            "valid": True,
        },
        {
            "id": 3,
            "parameter_type_id": 135_298,
            "value": "1234567",
            "constraint": None,
            "val_type": "int",
            "required": False,
            "valid": True,
        },
    ]
    result = await http_client.get(url, params=request)
    assert result.status_code == 200
    assert result.json() == response
