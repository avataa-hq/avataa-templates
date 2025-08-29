from application.template_object.read.dto import (
    TemplateObjectByIdRequestDTO,
    TemplateObjectRequestDTO,
)
from application.template_parameter.create.dto import (
    TemplateParameterCreateRequestDTO,
)
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.vo.template_object_by_id_filter import (
    TemplateObjectByIdFilter,
)
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.template_parameter.vo.template_parameter_exists import (
    TemplateParameterExists,
)


def template_object_filter_from_dto(
    request: TemplateObjectRequestDTO,
) -> TemplateObjectFilter:
    return TemplateObjectFilter(
        template_object_id=request.template_id,
        parent_object_id=request.parent_id,
        depth=request.depth,
    )


def template_object_by_id_from_dto(
    request: TemplateObjectByIdRequestDTO,
) -> TemplateObjectByIdFilter:
    return TemplateObjectByIdFilter(id=TemplateObjectId(request.id))


def template_parameter_exists_from_dto(
    request: TemplateParameterCreateRequestDTO,
) -> TemplateParameterExists:
    return TemplateParameterExists(
        template_object_id=TemplateObjectId(request.template_object_id),
        parameter_type_id=[
            ParameterTypeId(param.parameter_type_id) for param in request.data
        ],
    )
