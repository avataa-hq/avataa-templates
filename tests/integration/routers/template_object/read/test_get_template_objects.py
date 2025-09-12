from httpx import AsyncClient
import pytest

from config import setup_config
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId


@pytest.fixture(scope="session")
def base_url() -> str:
    return (
        f"{setup_config().app.prefix}/v{setup_config().app.app_version}/objects"
    )


@pytest.mark.asyncio(loop_scope="session")
async def test_search_template_object(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    tmo_id = 46_181
    template_id = 1
    to = TemplateObjectAggregate(
        id=TemplateObjectId(1),
        template_id=TemplateId(template_id),
        object_type_id=ObjectTypeId(tmo_id),
        required=True,
        valid=True,
    )
    mock_factory.template_object_reader_mock.get_tree_by_filter.return_value = [
        to
    ]
    param_1 = TemplateParameterAggregate(
        id=1,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_296),
        value="Value 1",
        constraint="Value 1",
        val_type="str",
        required=True,
        valid=True,
    )
    param_2 = TemplateParameterAggregate(
        id=2,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_297),
        value="[1, 2]",
        constraint=None,
        val_type="mo_link",
        required=False,
        valid=True,
    )
    param_3 = TemplateParameterAggregate(
        id=3,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_298),
        value="1234567",
        constraint=None,
        val_type="int",
        required=False,
        valid=True,
    )
    param_4 = TemplateParameterAggregate(
        id=4,
        template_object_id=TemplateObjectId(1),
        parameter_type_id=ParameterTypeId(135_299),
        value="123",
        constraint=None,
        val_type="str",
        required=True,
        valid=True,
    )
    mock_factory.template_parameter_reader_mock.get_by_template_object_ids.return_value = [
        param_1,
        param_2,
        param_3,
        param_4,
    ]

    request = {
        "template_id": template_id,
        "depth": 1,
        "include_parameters": True,
    }
    response = [
        {
            "id": 1,
            "object_type_id": tmo_id,
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
            "template_id": template_id,
            "children": [],
            "valid": True,
        }
    ]

    result = await http_client.get(base_url, params=request)
    assert result.status_code == 200
    assert result.json() == response


@pytest.mark.asyncio(loop_scope="session")
async def test_search_template_object_without_include(
    http_client: AsyncClient,
    base_url: str,
    mock_factory,
):
    tmo_id = 46_181
    template_id = 1
    to = TemplateObjectAggregate(
        id=TemplateObjectId(1),
        template_id=TemplateId(template_id),
        object_type_id=ObjectTypeId(tmo_id),
        required=True,
        valid=True,
    )
    mock_factory.template_object_reader_mock.get_tree_by_filter.return_value = [
        to
    ]

    request = {
        "template_id": template_id,
        "depth": 1,
        "include_parameters": False,
    }
    response = [
        {
            "id": 1,
            "object_type_id": tmo_id,
            "required": True,
            "parameters": [],
            "children": [],
            "template_id": template_id,
            "valid": True,
        }
    ]

    result = await http_client.get(base_url, params=request)
    assert result.status_code == 200
    assert result.json() == response
