from httpx import AsyncClient
import pytest

from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from exceptions import TemplateObjectNotFound
from models import TemplateObject


@pytest.fixture(scope="session")
def base_url() -> str:
    return (
        f"{setup_config().app.prefix}/v{setup_config().app.app_version}/objects"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_template_object(
    http_client: AsyncClient, base_url: str, mock_db, mock_factory
) -> None:
    # Assign
    template_object_id = 1
    template_id = 1
    object_type_id = 1
    full_url = f"{base_url}/{template_object_id}"
    to = TemplateObject(
        template_id=template_id,
        parent_object_id=None,
        object_type_id=object_type_id,
        required=False,
        valid=True,
    )
    to_aggr = TemplateObjectAggregate(
        id=TemplateObjectId(template_object_id),
        template_id=TemplateId(template_id),
        object_type_id=ObjectTypeId(object_type_id),
        required=False,
        valid=True,
    )
    to.id = template_object_id
    mock_db.execute.return_value.scalar_one_or_none.return_value = to
    mock_factory.to_reader_mock.get_by_id.return_value = to_aggr
    # Act
    result = await http_client.delete(full_url)
    # Assert
    assert result.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_template_object_not_found(
    http_client: AsyncClient, base_url: str, mock_db, mock_factory
) -> None:
    # Assign
    template_object_id = 1
    full_url = f"{base_url}/{template_object_id}"
    mock_db.execute.return_value.scalar_one_or_none.side_effect = (
        TemplateObjectNotFound()
    )
    mock_factory.to_reader_mock.get_by_id.side_effect = (
        TemplateObjectReaderApplicationException(
            status_code=404, detail="Template Object not found."
        )
    )
    response = {"detail": "Template object not found"}
    # Act
    result = await http_client.delete(full_url)
    # Assert
    assert result.status_code == 404
    assert result.json() == response
