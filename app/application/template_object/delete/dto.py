from dataclasses import dataclass


# From Router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateObjectDeleteRequestDTO:
    template_object_id: int
