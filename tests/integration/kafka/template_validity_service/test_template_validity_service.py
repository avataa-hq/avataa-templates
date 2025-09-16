from datetime import datetime, timedelta, timezone

import pytest

from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template.aggregate import TemplateAggregate
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.service import TemplateParameterValidityService
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId


@pytest.mark.asyncio(loop_scope="session")
async def test_update_tprm_with_no_change_val_type(
    container,
    mock_factory,
) -> None:
    # Assign
    tprm_id = 1
    template_parameter_id = 1
    template_object_id = 1
    old_val_type = "int"
    new_val_type = "int"
    tp_aggr = TemplateParameterAggregate(
        id=template_parameter_id,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value="7",
        required=False,
        val_type=old_val_type,
        valid=True,
    )
    to_aggr = TemplateObjectAggregate(
        id=TemplateObjectId(template_object_id),
        template_id=TemplateId(1),
        object_type_id=ObjectTypeId(1),
        required=False,
        valid=True,
    )
    mock_factory.tp_reader_mock.get_template_object_id_by_parameter_type_id.return_value = [
        tprm_id
    ]
    mock_factory.to_reader_mock.get_by_ids.return_value = [to_aggr]
    mock_factory.tp_reader_mock.get_by_template_object_ids.return_value = [
        tp_aggr
    ]
    async with container() as di:
        interactor = await di.get(TemplateParameterValidityService)

        # Act
        await interactor.validate(tprm_id, new_val_type)

        # Assert
        mock_factory.to_reader_mock.get_by_ids.assert_called_once_with(
            [tprm_id]
        )
        mock_factory.tp_reader_mock.get_by_template_object_ids.assert_called_once_with(
            [template_parameter_id]
        )
        mock_factory.tp_updater_mock.bulk_update_template_parameter.assert_not_called()
        mock_factory.to_updater_mock.update_template_object.assert_not_called()


@pytest.mark.asyncio(loop_scope="session")
async def test_update_tprm_with_change_val_type(
    container,
    mock_factory,
) -> None:
    # Assign
    tprm_id = 1
    tmo_id = 1
    template_parameter_id = 1
    template_object_id = 1
    template_id = 1
    name = "TestTemplate"
    owner = "Adm1n"
    cr_date = datetime.now(tz=timezone.utc)
    md_date = cr_date + timedelta(seconds=1)
    old_val_type = "int"
    new_val_type = "float"
    tp_aggr = TemplateParameterAggregate(
        id=template_parameter_id,
        template_object_id=TemplateObjectId(template_object_id),
        parameter_type_id=ParameterTypeId(tprm_id),
        value="7",
        required=False,
        val_type=old_val_type,
        valid=True,
    )
    to_aggr = TemplateObjectAggregate(
        id=TemplateObjectId(template_object_id),
        template_id=TemplateId(template_id),
        object_type_id=ObjectTypeId(tmo_id),
        required=False,
        valid=True,
    )
    t_aggr = TemplateAggregate(
        id=TemplateId(template_id),
        name=name,
        owner=owner,
        object_type_id=ObjectTypeId(tmo_id),
        creation_date=cr_date,
        modification_date=md_date,
        valid=True,
        version=1,
    )
    mock_factory.tp_reader_mock.get_template_object_id_by_parameter_type_id.return_value = [
        tprm_id
    ]
    mock_factory.to_reader_mock.get_by_ids.return_value = [to_aggr]
    mock_factory.to_reader_mock.get_reverse_tree_by_id.return_value = [to_aggr]
    mock_factory.tp_reader_mock.get_by_template_object_ids.return_value = [
        tp_aggr
    ]
    mock_factory.t_reader_mock.get_by_ids.return_value = [t_aggr]
    mock_factory.to_reader_mock.get_validity_by_template_id.return_value = [
        False
    ]
    async with container() as di:
        interactor = await di.get(TemplateParameterValidityService)

        # Act
        await interactor.validate(tprm_id, new_val_type)

        # Assert
        mock_factory.to_reader_mock.get_by_ids.assert_called_once_with(
            [tprm_id]
        )
        mock_factory.tp_reader_mock.get_by_template_object_ids.assert_called_once_with(
            [template_parameter_id]
        )
        mock_factory.tp_updater_mock.bulk_update_template_parameter.assert_called_once_with(
            [tp_aggr]
        )
        mock_factory.to_updater_mock.update_template_object.assert_called_once_with(
            to_aggr
        )
        mock_factory.t_reader_mock.get_by_ids.assert_called_once_with(
            [template_id]
        )
        mock_factory.to_reader_mock.get_validity_by_template_id.assert_called_once_with(
            template_id
        )
        mock_factory.t_updater_mock.update_template.assert_called_once_with(
            t_aggr
        )
