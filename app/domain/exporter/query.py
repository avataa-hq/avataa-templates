from io import BytesIO
from typing import Protocol

from domain.exporter.vo.enriched_export_data import (
    CompleteOTEnrichedExportData,
)
from domain.importer.vo.import_validation_result import ImportValidationResult


class DataFormatter(Protocol):
    def format_to_excel(
        self, request: CompleteOTEnrichedExportData
    ) -> BytesIO: ...

    def format_to_excel_with_errors(
        self, request: ImportValidationResult
    ) -> bytes: ...
