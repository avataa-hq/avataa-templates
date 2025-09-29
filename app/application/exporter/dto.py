from dataclasses import dataclass
from io import BytesIO


# From router
@dataclass(frozen=True, slots=True, kw_only=True)
class OTExportRequestDTO:
    template_ids: list[int]


# To router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateExportResponseDTO:
    excel_file: BytesIO
    filename: str
