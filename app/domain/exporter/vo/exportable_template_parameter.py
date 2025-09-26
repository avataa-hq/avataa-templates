from dataclasses import dataclass

from domain.template_parameter.aggregate import TemplateParameterAggregate


@dataclass(frozen=True, slots=True)
class ExportableTemplateParameter:
    aggregate: TemplateParameterAggregate
    template_object_type_name: str
    parameter_type_name: str
