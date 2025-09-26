from dataclasses import dataclass

from domain.template_object.aggregate import TemplateObjectAggregate


@dataclass(frozen=True, slots=True)
class ExportableTemplateObject:
    aggregate: TemplateObjectAggregate

    template_name: str
    object_type_name: str

    parent_object_name: str | None = None
