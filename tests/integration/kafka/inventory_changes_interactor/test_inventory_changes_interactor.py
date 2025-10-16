import pytest

from application.inventory_changes.interactors import InventoryChangesInteractor


@pytest.mark.asyncio(loop_scope="session")
async def test_update_tprm(
    container,
    mock_factory,
) -> None:
    # Assign
    obj_id = 141029
    multiple_value = False
    val_type = "int"

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
                        "id": obj_id,
                        "modification_date": "2025-09-11T09:04:56.333488",
                        "modified_by": "test_client",
                        "multiple": multiple_value,
                        "name": "Score",
                        "prm_link_filter": "",
                        "required": False,
                        "returnable": False,
                        "tmo_id": 46181,
                        "val_type": val_type,
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

        # Assert
        mock_factory.tp_validity_service_mock.invalid_by_tprm.assert_not_called()
        mock_factory.tp_validity_service_mock.invalid_by_tmo.assert_not_called()
        mock_factory.tp_validity_service_mock.validate.assert_called_once_with(
            obj_id, val_type, multiple_value
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_tprm(
    container,
    mock_factory,
) -> None:
    test_messages = [
        (
            {
                "objects": [
                    {
                        "created_by": "Anonymous",
                        "creation_date": "2025-09-11T19:32:55.182626",
                        "description": "",
                        "geometry_type": "",
                        "global_uniqueness": False,
                        "icon": "",
                        "id": 5,
                        "label": [],
                        "latitude": 0,
                        "lifecycle_process_definition": "",
                        "longitude": 0,
                        "materialize": True,
                        "minimize": False,
                        "modification_date": "2025-09-11T19:32:55.182655",
                        "modified_by": "Anonymous",
                        "name": "InnerInnerTMO",
                        "p_id": 2,
                        "points_constraint_by_tmo": [],
                        "primary": [],
                        "severity_id": 0,
                        "status": 0,
                        "version": 1,
                        "virtual": False,
                    }
                ]
            },
            "TMO",
            "deleted",
        ),
        (
            {
                "objects": [
                    {
                        "constraint": "",
                        "created_by": "Anonymous",
                        "creation_date": "2025-09-11T19:33:18.468550",
                        "description": "",
                        "field_value": "",
                        "group": "",
                        "id": 12,
                        "modification_date": "2025-09-11T19:33:18.468569",
                        "modified_by": "Anonymous",
                        "multiple": False,
                        "name": "tprm_5",
                        "prm_link_filter": "",
                        "required": False,
                        "returnable": True,
                        "tmo_id": 5,
                        "val_type": "int",
                        "version": 1,
                    },
                    {
                        "constraint": "",
                        "created_by": "Anonymous",
                        "creation_date": "2025-09-11T19:33:24.900207",
                        "description": "",
                        "field_value": "",
                        "group": "",
                        "id": 13,
                        "modification_date": "2025-09-11T19:33:24.900229",
                        "modified_by": "Anonymous",
                        "multiple": False,
                        "name": "tprm_6",
                        "prm_link_filter": "",
                        "required": False,
                        "returnable": True,
                        "tmo_id": 5,
                        "val_type": "int",
                        "version": 1,
                    },
                ]
            },
            "TPRM",
            "deleted",
        ),
    ]

    async with container() as di:
        interactor = await di.get(InventoryChangesInteractor)

        # Act
        await interactor(test_messages)

        # Assert
        mock_factory.tp_validity_service_mock.invalid_by_tprm.assert_called_once_with(
            [12, 13]
        )
        mock_factory.tp_validity_service_mock.invalid_by_tmo.assert_called_once_with(
            [5]
        )
        mock_factory.tp_validity_service_mock.validate.assert_not_called()
