from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/registry-template"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "name, owner, object_type_id, t_id, status_code",
    [
        ("template_1", "Adm1n", 1, 1, 200),
        ("template_1", "Adm1n", 0, 1, 422),
    ],
)
async def test_create_template(
    http_client: AsyncClient,
    base_url: str,
    name: str,
    owner: str,
    object_type_id: int,
    t_id: int,
    status_code: int,
    mock_db,
):
    # Arrange
    request = {
        "name": name,
        "owner": owner,
        "object_type_id": object_type_id,
    }
    # Act
    result = await http_client.post(base_url, json=request)

    # Assert
    assert result.status_code == status_code
    if status_code == 200:
        assert result.json()["name"] == name
        assert result.json()["owner"] == owner
        assert result.json()["object_type_id"] == object_type_id
        assert result.json()["id"] == t_id
