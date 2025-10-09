from dataclasses import dataclass

from domain.importer.vo.validation_result import ValidationResult


# From router
@dataclass(frozen=True, slots=True, kw_only=True)
class OTImportRequestDTO:
    file_data: bytes
    owner: str


# To router
@dataclass(frozen=True, slots=True, kw_only=True)
class OTImportResponseDTO:
    data_file: bytes
    filename: str
    result: ValidationResult
