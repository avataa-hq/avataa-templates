from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models import Template, TemplateObject
from services.inventory_services.protocols import (
    TemplateObjectRepo,
)


@pytest.mark.asyncio
async def test_template_objects_invalid(
    test_session: AsyncSession,
) -> None:
    # Arrange
    repo = TemplateObjectRepo(session=test_session)

    template = Template(
        name="Test Template",
        owner="Test Owner",
        object_type_id=1,
        creation_date=datetime.now(),
        modification_date=datetime.now(),
        version=1,
        valid=True,
        template_objects=[],
    )
    test_session.add(template)
    await test_session.flush()

    template_objects = [
        TemplateObject(
            template_id=template.id,
            parent_object_id=None,
            object_type_id=1,
            required=False,
            parameters=[],
        ),
        TemplateObject(
            template_id=template.id,
            parent_object_id=None,
            object_type_id=1,
            required=False,
            parameters=[],
        ),
    ]

    for obj in template_objects:
        test_session.add(obj)
    await test_session.flush()

    # Act
    objects = await repo.get_template_objects_by_object_type_id([1])
    updated_objects = await repo.set_template_objects_invalid(objects)
    await test_session.commit()

    # Assert
    assert len(updated_objects) == 2
    for obj in updated_objects:
        assert obj.valid is False


@pytest.mark.asyncio
async def test_template_objects_invalid_id(
    test_session: AsyncSession,
) -> None:
    # Arrange
    repo = TemplateObjectRepo(session=test_session)

    template = Template(
        name="Test Template",
        owner="Test Owner",
        object_type_id=1,
        creation_date=datetime.now(),
        modification_date=datetime.now(),
        version=1,
        valid=True,
        template_objects=[],
    )
    test_session.add(template)
    await test_session.flush()

    template_objects = [
        TemplateObject(
            template_id=template.id,
            parent_object_id=None,
            object_type_id=1,
            required=False,
            parameters=[],
        )
    ]

    for obj in template_objects:
        test_session.add(obj)
    await test_session.flush()

    # Act
    objects = await repo.get_template_objects_by_object_type_id([17])

    # Assert
    assert len(objects) == 0
