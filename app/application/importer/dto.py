from dataclasses import dataclass


# From router
@dataclass(frozen=True, slots=True, kw_only=True)
class OTImportRequestDTO:
    file_data: bytes
    owner: str
