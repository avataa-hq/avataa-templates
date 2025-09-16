from dataclasses import dataclass


# From Router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateParameterDeleteRequestDTO:
    template_parameter_id: int
