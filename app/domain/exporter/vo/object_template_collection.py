from dataclasses import dataclass
from datetime import datetime

from domain.exporter.vo.exportable_template import ExportableTemplate
from domain.exporter.vo.exportable_template_object import (
    ExportableTemplateObject,
)
from domain.exporter.vo.exportable_template_parameter import (
    ExportableTemplateParameter,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ExportableTemplatesCollection:
    templates: list[ExportableTemplate]
    template_objects: list[ExportableTemplateObject]
    template_parameters: list[ExportableTemplateParameter]
    exported_at: datetime
