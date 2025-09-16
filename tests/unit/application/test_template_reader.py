from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from application.template.read.dto import (
    TemplateRequestDTO,
    TemplateResponseDTO,
)
from application.template.read.interactors import TemplateReaderInteractor
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.template.aggregate import TemplateAggregate


@pytest.mark.asyncio
async def test_template_reader_interactor_returns_expected_response():
    # Arrange
    mock_repo = AsyncMock()
    interactor = TemplateReaderInteractor(t_repo=mock_repo)  # noqa

    request = TemplateRequestDTO(
        name="test_name",
        owner="test_owner",
        object_type_id=1,
        limit=10,
        offset=0,
    )

    fake_template = TemplateAggregate(
        id=TemplateId(1),
        name="template1",
        owner="test_owner",
        object_type_id=ObjectTypeId(1),
        creation_date=datetime.now(tz=timezone.utc),
        modification_date=datetime.now(tz=timezone.utc),
        valid=True,
        version=1,
    )

    mock_repo.get_template_by_filter.return_value = [fake_template]

    # Act
    result = await interactor(request)

    # Assert
    assert isinstance(result, TemplateResponseDTO)
    assert len(result.data) == 1
    assert result.data[0].name == "template1"
    mock_repo.get_template_by_filter.assert_awaited_once()
