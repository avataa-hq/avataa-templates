import pytest

from application.inventory_changes.interactors import InventoryChangesInteractor


@pytest.mark.asyncio(loop_scope="session")
async def test_update_tprm(
    container,
    mock_factory,
) -> None:
    # Assign
    test_messages = [
        (
            {
                "objects": [
                    {
                        "constraint": "",
                        "created_by": "test_client",
                        "creation_date": "2025-08-18T10:01:09.079526",
                        "description": "",
                        "field_value": "",
                        "group": "",
                        "id": 141029,
                        "modification_date": "2025-09-11T09:04:56.333488",
                        "modified_by": "test_client",
                        "multiple": False,
                        "name": "Score",
                        "prm_link_filter": "",
                        "required": False,
                        "returnable": False,
                        "tmo_id": 46181,
                        "val_type": "int",
                        "version": 73,
                    }
                ]
            },
            "TPRM",
            "updated",
        )
    ]
    mock_factory.to_service_mock.set_template_object_invalid.return_value = None
    mock_factory.tp_service_mock.set_template_parameter_invalid.return_value = (
        None
    )
    mock_factory.uow_mock.commit.return_value = None

    async with container() as di:
        interactor = await di.get(InventoryChangesInteractor)

        # Act
        await interactor(test_messages)
