from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from models import TemplateObject


@pytest.fixture(scope="session")
def url() -> str:
    return (
        f"{setup_config().app.prefix}/v{setup_config().app.app_version}/objects"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_parameter(
    http_client: AsyncClient,
    url: str,
    mock_db,
    mock_factory,
) -> None:
    template_object_id = 1
    template_id = 1
    object_type_id = 1
    required_before = False
    required_after = not required_before
    valid = True
    full_url = f"{url}/{template_object_id}"
    to = TemplateObject(
        template_id=template_id,
        parent_object_id=None,
        object_type_id=object_type_id,
        required=required_before,
        valid=valid,
    )
    to.id = template_object_id
    mock_db.execute.return_value.scalar_one_or_none.return_value = to
    to_aggr = TemplateObjectAggregate(
        id=TemplateObjectId(template_object_id),
        template_id=TemplateId(template_id),
        object_type_id=ObjectTypeId(object_type_id),
        required=required_before,
        valid=valid,
    )
    mock_factory.template_object_reader_mock.get_by_id.return_value = to_aggr
    request = {
        "required": required_after,
    }
    response = {
        "id": template_object_id,
        "object_type_id": object_type_id,
        "template_id": template_id,
        "parent_object_id": None,
        "required": required_after,
        "valid": valid,
    }

    result = await http_client.put(full_url, json=request)

    assert result.status_code == 200
    assert result.json() == response
