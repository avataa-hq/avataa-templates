from unittest.mock import AsyncMock

from httpx import AsyncClient
import pytest

from application.paramater_validation.exceptions import (
    ParameterValidationException,
)
from config import setup_config
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId


@pytest.fixture(scope="session")
def url() -> str:
    return f"{setup_config().app.prefix}/v{setup_config().app.app_version}/add-parameters"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter(
    http_client: AsyncClient,
    url: str,
    fake_tp_repo_create: AsyncMock,
    fake_tp_repo_read: AsyncMock,
    fake_to_repo: AsyncMock,
):
    template_object_id = 1
    tprm_id = 135_299
    val = "123"
    full_url = f"{url}/{template_object_id}"
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=True,
        val_type="str",
        valid=True,
        constraint=None,
    )
    fake_tp_repo_read.exists.return_value = False
    fake_tp_repo_create.create_template_parameters.return_value = [param_1]

    fake_to_repo.get_object_type_by_id.return_value = 46_181
    request = [{"parameter_type_id": tprm_id, "value": val, "required": True}]
    response = [
        {
            "id": 1,
            "parameter_type_id": tprm_id,
            "value": val,
            "constraint": None,
            "required": True,
            "val_type": "str",
            "valid": True,
        }
    ]
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("val", ["[False, True]", "[false, true]"])
async def test_create_template_parameter_multiple_bool(
    http_client: AsyncClient,
    url: str,
    val: str,
    fake_tp_repo_create: AsyncMock,
    fake_tp_repo_read: AsyncMock,
    fake_to_repo: AsyncMock,
):
    template_object_id = 1
    full_url = f"{url}/{template_object_id}"
    tprm_id = 141_047
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=False,
        val_type="bool",
        valid=True,
        constraint=None,
    )
    fake_tp_repo_read.exists.return_value = False
    fake_tp_repo_create.create_template_parameters.return_value = [param_1]
    fake_to_repo.get_object_type_by_id.return_value = 46_181

    request = [{"parameter_type_id": tprm_id, "value": val, "required": False}]
    response = [
        {
            "id": 1,
            "parameter_type_id": tprm_id,
            "value": val,
            "constraint": None,
            "required": False,
            "val_type": "bool",
            "valid": True,
        }
    ]
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter_with_already_exists_parameter(
    http_client: AsyncClient,
    url: str,
    fake_tp_repo_create: AsyncMock,
    fake_tp_repo_read: AsyncMock,
    fake_to_repo: AsyncMock,
):
    template_object_id = 1
    tprm_id = 135_299
    val = "123"
    full_url = f"{url}/{template_object_id}"
    fake_tp_repo_read.exists.return_value = True

    request = [{"parameter_type_id": tprm_id, "value": val, "required": True}]
    response = {"detail": "The template parameter(s) already exist(s)."}
    result = await http_client.post(full_url, json=request)
    assert result.status_code == 422
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_create_template_parameter_from_incorrect_tmo(
    http_client: AsyncClient,
    url: str,
    fake_tp_repo_create: AsyncMock,
    fake_tp_repo_read: AsyncMock,
    fake_to_repo: AsyncMock,
    mock_trpm_validator: AsyncMock,
):
    val = "1"
    template_object_id = 1
    full_url = f"{url}/{template_object_id}"
    tprm_id = 100
    status_code = 422
    detail_error = f"Inconsistent request parameters: {[tprm_id]} do not belong tmo {template_object_id}."

    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value=val,
        required=False,
        val_type="bool",
        valid=True,
        constraint=None,
    )
    fake_tp_repo_read.exists.return_value = False
    fake_tp_repo_create.create_template_parameters.return_value = [param_1]
    fake_to_repo.get_object_type_by_id.return_value = 46_181
    mock_trpm_validator.side_effect = ParameterValidationException(
        status_code=status_code,
        detail=detail_error,
    )

    request = [
        {"parameter_type_id": tprm_id + 1, "value": val, "required": False}
    ]

    result = await http_client.post(full_url, json=request)
    assert result.status_code == status_code
    assert result.json() == {"detail": detail_error}
