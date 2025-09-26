from dataclasses import dataclass
from io import BytesIO


# From router
@dataclass
class OTExportRequestDTO:
    template_ids: list[int]


# To router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateExportResponseDTO:
    excel_file: BytesIO
    filename: str
