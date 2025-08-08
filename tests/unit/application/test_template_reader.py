from datetime import datetime, timezone

import pytest
from unittest.mock import AsyncMock

from application.template.reader.interactors import TemplateReaderInteractor
from application.template.reader.dto import (
    TemplateRequestDTO,
    TemplateResponseDTO,
)
from domain.template.template import TemplateAggregate


@pytest.mark.asyncio
async def test_template_reader_interactor_returns_expected_response():
    # Arrange
    mock_gateway = AsyncMock()
    interactor = TemplateReaderInteractor(gateway=mock_gateway)  # noqa

    request = TemplateRequestDTO(
        name="test_name",
        owner="test_owner",
        object_type_id=1,
        limit=10,
        offset=0,
    )

    fake_template = TemplateAggregate(
        id=1,
        name="template1",
        owner="test_owner",
        object_type_id=1,
        creation_date=datetime.now(tz=timezone.utc),
        modification_date=datetime.now(tz=timezone.utc),
        valid=True,
        version=1,
    )

    mock_gateway.get_template_by_filter.return_value = [fake_template]

    # Act
    result = await interactor(request)

    # Assert
    assert isinstance(result, TemplateResponseDTO)
    assert len(result.data) == 1
    assert result.data[0].name == "template1"
    mock_gateway.get_template_by_filter.assert_awaited_once()
