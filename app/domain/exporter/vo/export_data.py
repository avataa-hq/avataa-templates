from dataclasses import dataclass
from datetime import datetime

from domain.template.aggregate import TemplateAggregate
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_parameter.aggregate import TemplateParameterAggregate


@dataclass(frozen=True, slots=True, kw_only=True)
class CompleteOTExportData:
    templates: list[TemplateAggregate]
    template_objects: list[TemplateObjectAggregate]
    template_parameters: list[TemplateParameterAggregate]
    exported_at: datetime
