from dataclasses import dataclass

from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId


@dataclass(frozen=True, slots=True)
class TemplateParameterExists:
    template_object_id: TemplateObjectId
    parameter_type_id: list[ParameterTypeId]
