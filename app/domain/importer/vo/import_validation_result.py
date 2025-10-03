from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ImportValidationResult:
    is_valid: bool
    error: str
