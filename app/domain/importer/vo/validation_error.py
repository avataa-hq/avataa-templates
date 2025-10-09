from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)  # Immutable VO
class ValidationErrorMessage:
    message: str
    sheet_name: str | None
    row: int | None = None
    column: str | None = None
    # field: str | None = None
