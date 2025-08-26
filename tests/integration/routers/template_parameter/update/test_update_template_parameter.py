from unittest.mock import AsyncMock

from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId


@pytest.fixture(scope="session")
def url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_parameter(
    http_client: AsyncClient,
    url: str,
    fake_tp_repo: AsyncMock,
    fake_to_repo: AsyncMock,
    fake_tp_update: AsyncMock,
):
    template_parameter_id = 1
    tprm_id = 141_046
    val = "[8]"
    required_value = False
    val_type_value = "int"
    full_url = f"{url}/{template_parameter_id}"
    fake_tp_repo.get_by_id.return_value = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_parameter_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=True,
        val_type=val_type_value,
        valid=True,
        constraint="",
    )
    fake_to_repo.get_object_type_by_id.return_value = 46_181
    request = {
        "parameter_type_id": tprm_id,
        "value": val,
        "required": required_value,
    }
    response = {
        "id": 1,
        "parameter_type_id": tprm_id,
        "value": val,
        "constraint": None,
        "required": required_value,
        "val_type": val_type_value,
        "valid": True,
    }

    result = await http_client.put(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response
