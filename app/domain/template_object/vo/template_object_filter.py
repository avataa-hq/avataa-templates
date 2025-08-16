from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateObjectFilter:
    template_id: int
    depth: int
    include_parameters: bool

    parent_object_id: int | None

    limit: int = 50
    offset: int = 0
