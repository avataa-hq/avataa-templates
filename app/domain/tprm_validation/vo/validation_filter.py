from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParameterValidationFilter:
    tmo_id: int
