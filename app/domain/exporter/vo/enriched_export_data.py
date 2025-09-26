from datetime import datetime

from domain.exporter.vo.exportable_template import ExportableTemplate
from domain.exporter.vo.exportable_template_object import (
    ExportableTemplateObject,
)
from domain.exporter.vo.exportable_template_parameter import (
    ExportableTemplateParameter,
)


class CompleteOTEnrichedExportData:
    def __init__(
        self,
        templates: list[ExportableTemplate],
        template_objects: list[ExportableTemplateObject],
        template_parameters: list[ExportableTemplateParameter],
        exported_at: datetime,
    ):
        self.templates = templates
        self.template_objects = template_objects
        self.template_parameters = template_parameters
        self.exported_at = exported_at
