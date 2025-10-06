from dataclasses import dataclass


@dataclass(frozen=True)  # Immutable VO
class ValidationError:
    message: str
    sheet_name: str | None
    row: int | None = None
    column: int | None = None
    field: str | None = None
