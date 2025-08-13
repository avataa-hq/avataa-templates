from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateFilter:
    name: str | None = None
    owner: str | None = None
    object_type_id: int | None = None

    limit: int = 50
    offset: int = 0
