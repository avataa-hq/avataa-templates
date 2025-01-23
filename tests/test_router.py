import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_registry_template(
    async_client: AsyncClient, mock_grpc_response
) -> None:
    (
        get_all_tmo_data_from_inventory,
        get_all_tprms,
    ) = mock_grpc_response
    get_all_tmo_data_from_inventory.return_value = [
        {"id": 100, "p_id": None},
        {"id": 200, "p_id": 100},
    ]
    get_all_tprms.return_value = [
        {
            "id": 1,
            "val_type": "string",
            "constraint": None,
            "required": True,
            "multiple": False,
        }
    ]

    response = await async_client.post(
        "/registry-template",
        json={
            "name": "Test Template",
            "owner": "test_user",
            "object_type_id": 100,
            "template_objects": [
                {
                    "object_type_id": 200,
                    "required": True,
                    "parameters": [
                        {
                            "parameter_type_id": 1,
                            "value": "test value",
                            "required": True,
                        }
                    ],
                }
            ],
        },
    )

    assert response.status_code == 200
    print(response.json())
