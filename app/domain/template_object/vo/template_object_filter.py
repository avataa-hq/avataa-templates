from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateObjectFilter:
    template_id: int

    parent_object_id: int | None = None

    depth: int = 1

    limit: int = 100
    offset: int = 0
