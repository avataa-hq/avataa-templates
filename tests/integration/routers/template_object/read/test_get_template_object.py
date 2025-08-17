from unittest.mock import Mock

from httpx import AsyncClient
import pytest

from config import setup_config
from models import TemplateObject, TemplateParameter


@pytest.fixture(scope="session")
def url() -> str:
    return (
        f"{setup_config().app.prefix}/v{setup_config().app.app_version}/objects"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_search_template_parameter(
    http_client: AsyncClient, url: str, mock_db, app, fake_to_repo, fake_tp_repo
):
    first_result = Mock()
    first_result.scalar_one_or_none.return_value = {
        "id": 1,
        "template_id": 1,
        "parent_object_id": None,
        "object_type_id": 46181,
        "required": True,
        "valid": True,
    }

    session_scalars = Mock()
    scalars_all = Mock()
    param_1 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_296,
        value="Value 1",
        constraint="Value 1",
        val_type="str",
        required=True,
        valid=True,
    )
    param_1.id = 1
    param_2 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_297,
        value="[1, 2]",
        constraint=None,
        val_type="mo_link",
        required=False,
        valid=True,
    )
    param_2.id = 2
    param_3 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_298,
        value="1234567",
        constraint=None,
        val_type="int",
        required=False,
        valid=True,
    )
    param_3.id = 3
    param_4 = TemplateParameter(
        template_object_id=1,
        parameter_type_id=135_299,
        value="123",
        constraint=None,
        val_type="str",
        required=True,
        valid=True,
    )
    param_4.id = 4
    obj_1 = TemplateObject(
        template_id=1,
        object_type_id=46181,
        parent_object_id=None,
        required=True,
        valid=True,
        parameters=[param_1, param_2, param_3, param_4],
    )
    obj_1.id = 1

    scalars_all.all.return_value = [obj_1]
    session_scalars.scalars.return_value = scalars_all
    mock_db.execute.side_effect = [first_result, session_scalars]
    mock_db.scalars.return_value = scalars_all

    request = {"template_id": 1, "depth": 1, "include_parameters": True}
    response = [
        {
            "id": 1,
            "object_type_id": 46181,
            "required": True,
            "parameters": [
                {
                    "id": 1,
                    "parameter_type_id": 135296,
                    "value": "Value 1",
                    "constraint": "Value 1",
                    "required": True,
                    "val_type": "str",
                    "valid": True,
                },
                {
                    "id": 2,
                    "parameter_type_id": 135297,
                    "value": "[1, 2]",
                    "constraint": None,
                    "required": False,
                    "val_type": "mo_link",
                    "valid": True,
                },
                {
                    "id": 3,
                    "parameter_type_id": 135298,
                    "value": "1234567",
                    "constraint": None,
                    "required": False,
                    "val_type": "int",
                    "valid": True,
                },
                {
                    "id": 4,
                    "parameter_type_id": 135299,
                    "value": "123",
                    "constraint": None,
                    "required": True,
                    "val_type": "str",
                    "valid": True,
                },
            ],
            "children": [],
            "valid": True,
        }
    ]

    result = await http_client.get(url, params=request)
    assert result.status_code == 200
    assert result.json() == response
    app.dependency_overrides.clear()


@pytest.mark.asyncio(loop_scope="session")
async def test_search_template_parameter_without_include(
    http_client: AsyncClient, url: str, mock_db
):
    request = {"template_id": 1, "depth": 1, "include_parameters": False}
    response = [
        {
            "id": 1,
            "object_type_id": 46181,
            "required": True,
            "parameters": [],
            "children": [],
            "valid": True,
        }
    ]
    first_result = Mock()
    session_scalars = Mock()
    scalars_all = Mock()
    first_result.scalar_one_or_none.return_value = {
        "id": 1,
        "template_id": 1,
        "parent_object_id": None,
        "object_type_id": 46181,
        "required": True,
        "valid": True,
    }
    obj_1 = TemplateObject(
        template_id=1,
        parent_object_id=None,
        object_type_id=46181,
        required=True,
        valid=True,
    )
    obj_1.id = 1

    scalars_all.all.return_value = [obj_1]
    session_scalars.scalars.return_value = scalars_all
    mock_db.execute.side_effect = [first_result, session_scalars]
    mock_db.scalars.return_value = scalars_all

    result = await http_client.get(url, params=request)
    assert result.status_code == 200
    assert result.json() == response
