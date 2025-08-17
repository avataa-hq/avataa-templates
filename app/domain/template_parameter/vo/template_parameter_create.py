from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateParameterCreate:
    template_object_id: int
    parameter_type_id: int
    required: bool
    val_type: str

    value: str | None = None
    constraint: str | None = None
