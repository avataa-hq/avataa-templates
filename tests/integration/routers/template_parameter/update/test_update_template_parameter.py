from unittest.mock import AsyncMock

from httpx import AsyncClient
import pytest

from config import setup_config


@pytest.fixture(scope="session")
def url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_template_parameter(
    http_client: AsyncClient,
    url: str,
    fake_tp_repo: AsyncMock,
    fake_to_repo: AsyncMock,
):
    template_parameter_id = 1
    tprm_id = 141_046
    val = "[8]"
    full_url = f"{url}/{template_parameter_id}"
    # param_1 = TemplateParameterAggregate(
    #     id=1,
    #     template_object_id=TemplateObjectId(template_object_id),
    #     parameter_type_id=ParameterTypeId(tprm_id),
    #     value=val,
    #     required=False,
    #     val_type="int",
    #     valid=True,
    #     constraint=None,
    # )
    # fake_tp_repo.create_template_parameters.return_value = [param_1]
    #
    # fake_to_repo.get_object_type_by_id.return_value = 46_181
    request = {"parameter_type_id": tprm_id, "value": val, "required": False}
    response = {
        "id": 1,
        "parameter_type_id": tprm_id,
        "value": val,
        "constraint": None,
        "required": False,
        "val_type": "int",
        "valid": True,
    }

    result = await http_client.put(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response
