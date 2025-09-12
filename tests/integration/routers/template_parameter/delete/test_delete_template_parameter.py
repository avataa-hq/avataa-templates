from httpx import AsyncClient
import pytest

from application.template_parameter.read.exceptions import (
    TemplateParameterReaderApplicationException,
)
from config import setup_config
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from exceptions import TemplateParameterNotFound
from models import TemplateParameter


@pytest.fixture(scope="session")
def base_url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_template_parameter(
    http_client: AsyncClient, base_url: str, mock_db, mock_factory
) -> None:
    # Assign
    template_parameter_id = 1
    template_object_id = 1
    parameter_type_id = 1
    full_url = f"{base_url}/{template_parameter_id}"
    tp = TemplateParameter(
        template_object_id=template_object_id,
        parameter_type_id=parameter_type_id,
        value="1",
        constraint=None,
        val_type="str",
        required=False,
        valid=True,
    )
    tp.id = template_parameter_id
    tp_aggr = TemplateParameterAggregate(
        id=template_parameter_id,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(parameter_type_id),
        value="1",
        required=False,
        val_type="str",
        valid=True,
        constraint=None,
    )
    mock_db.execute.return_value.scalar_one_or_none.return_value = tp
    mock_factory.tp_reader_mock.get_by_id.return_value = tp_aggr

    # Act
    result = await http_client.delete(full_url)
    # Assert
    assert result.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_template_parameter_not_found(
    http_client: AsyncClient, base_url: str, mock_db, mock_factory
) -> None:
    # Assign
    template_parameter_id = 1
    full_url = f"{base_url}/{template_parameter_id}"
    mock_db.execute.return_value.scalar_one_or_none.side_effect = (
        TemplateParameterNotFound()
    )
    mock_factory.tp_reader_mock.get_by_id.side_effect = (
        TemplateParameterReaderApplicationException(
            status_code=404, detail="Template Parameter not found."
        )
    )
    response = {"detail": "Template parameter not found"}
    # Act
    result = await http_client.delete(full_url)
    # Assert
    assert result.status_code == 404
    assert result.json() == response
