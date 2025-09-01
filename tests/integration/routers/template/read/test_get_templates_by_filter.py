from datetime import datetime, timezone

from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.template.aggregate import TemplateAggregate


@pytest.fixture(scope="session")
def url() -> str:
    return (
        f"{setup_config().app.prefix}/v{setup_config().app.app_version}/search"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_search_template_object(
    http_client: AsyncClient,
    url: str,
    mock_factory,
):
    # Assign
    tmo_id = 46_181
    template_id = 1
    name = "Test Template"
    owner = "Adm1n"
    cur_date = datetime.now(tz=timezone.utc)

    format_time = "%Y-%m-%dT%H:%M:%S.%fZ"
    request = {"object_type_id": tmo_id, "limit": 50, "offset": 0}

    response = {
        "data": [
            {
                "id": template_id,
                "name": name,
                "owner": owner,
                "object_type_id": tmo_id,
                "creation_date": datetime.strftime(cur_date, format_time),
                "modification_date": datetime.strftime(cur_date, format_time),
                "valid": True,
                "version": 1,
            }
        ]
    }

    template = TemplateAggregate(
        id=TemplateId(template_id),
        name=name,
        owner=owner,
        object_type_id=ObjectTypeId(tmo_id),
        creation_date=cur_date,
        modification_date=cur_date,
        valid=True,
        version=1,
    )
    mock_factory.template_reader_mock.get_template_by_filter.return_value = [
        template
    ]
    # Act
    result = await http_client.post(url, json=request)
    # Assert
    assert result.status_code == 200
    assert result.json() == response
