from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.template_object.read.dto import TemplateObjectRequestDTO
from application.template_object.read.mapper import (
    template_object_filter_from_dto,
)
from infrastructure.db.template_object.read.gateway import (
    SQLTemplateObjectReaderRepository,
)
from models import Template, TemplateObject


@pytest.mark.asyncio
async def test_template_objects_invalid(
    test_session: AsyncSession,
) -> None:
    # Arrange
    gateway = SQLTemplateObjectReaderRepository(session=test_session)

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

    template_objects_raw = [
        TemplateObject(
            template_id=template.id,
            parent_object_id=None,
            object_type_id=1,
            required=False,
            parameters=[],
        ),
    ]

    for obj in template_objects_raw:
        test_session.add(obj)
    await test_session.flush()
    request = TemplateObjectRequestDTO(
        template_id=1,
        depth=1,
        include_parameters=False,
    )
    template_objects_filters = template_object_filter_from_dto(request)
    # Act
    objects = await gateway.get_object_type_by_id(template_objects_filters)
    await test_session.commit()

    # Assert
    assert objects
