from dataclasses import dataclass

from domain.template.aggregate import TemplateAggregate


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportableTemplate:
    aggregate: TemplateAggregate
    object_type_name: str
