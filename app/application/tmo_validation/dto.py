from dataclasses import dataclass


# From Application
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateObjectValidationRequestDTO:
    object_type_id: int
    parent_object_type_id: int | None = None
