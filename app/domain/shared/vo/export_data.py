from datetime import datetime

from domain.template.aggregate import TemplateAggregate
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_parameter.aggregate import TemplateParameterAggregate


class CompleteOTExportData:
    def __init__(
        self,
        templates: list[TemplateAggregate],
        template_objects: list[TemplateObjectAggregate],
        template_parameters: list[TemplateParameterAggregate],
        exported_at: datetime,
    ):
        self.templates = templates
        self.template_objects = template_objects
        self.template_parameters = template_parameters
        self.exported_at = exported_at
