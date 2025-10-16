from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate


@pytest.fixture(scope="session")
def base_url() -> str:
    return (
        f"{setup_config().app.prefix}/v{setup_config().app.app_version}/object"
    )


@pytest.mark.asyncio(loop_scope="session")
async def ptest_search_template_object_by_object_type_id(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
) -> None:
    # Assign
    object_type_id = 1
    template_id = 1
    template_object_id = 1
    request = {
        "object_type_id": object_type_id,
    }
    to_aggregate = TemplateObjectAggregate(
        id=TemplateObjectId(template_object_id),
        template_id=TemplateId(template_id),
        object_type_id=ObjectTypeId(object_type_id),
        required=False,
        valid=True,
        parent_object_id=None,
        children=[],
    )
    response = [
        {
            "id": template_object_id,
            "object_type_id": object_type_id,
            "required": True,
            "parameters": [],
            "template_id": template_id,
            "valid": True,
        }
    ]
    mock_factory.to_reader_mock.get_by_object_type_id.return_value = [
        to_aggregate
    ]
    # Act
    result = await http_client.get(base_url, params=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response
