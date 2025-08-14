from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateParameterFilter:
    template_object_id: int

    limit: int
    offset: int
