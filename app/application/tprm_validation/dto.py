from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateParameterValidationDTO:
    parameter_type_id: int
    required: bool

    value: str | None = None
    constraint: str | None = None


# From Application
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateParameterValidationRequestDTO:
    object_type_id: int
    parameter_to_validate: list[TemplateParameterValidationDTO]


# To Application
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateParameterWithTPRMData:
    parameter_type_id: int
    required: bool
    val_type: str
    multiple: bool

    value: str | None = None
    constraint: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateParameterValidationResponseDTO:
    valid_items: list[TemplateParameterWithTPRMData]
    invalid_items: list[TemplateParameterWithTPRMData]
    errors: list[str]
