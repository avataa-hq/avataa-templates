from application.template_parameter.update.dto import (
    TemplateParameterBulkUpdateRequestDTO,
    TemplateParameterDataUpdateRequestDTO,
)
from application.tprm_validation.dto import (
    TemplateParameterValidationDTO,
    TemplateParameterValidationRequestDTO,
)
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.template_parameter.vo.template_parameter_exists import (
    TemplateParameterExists,
)


def template_parameter_to_validator(
    obj_type_id: int,
    data: list[TemplateParameterDataUpdateRequestDTO],
) -> TemplateParameterValidationRequestDTO:
    return TemplateParameterValidationRequestDTO(
        object_type_id=obj_type_id,
        parameter_to_validate=[
            TemplateParameterValidationDTO(
                parameter_type_id=el.parameter_type_id,
                value=el.value,
                required=el.required,
                constraint=el.constraint,
            )
            for el in data
        ],
    )


def template_parameter_bulk_from_dto(
    request: TemplateParameterBulkUpdateRequestDTO,
) -> TemplateParameterExists:
    return TemplateParameterExists(
        template_object_id=TemplateObjectId(request.template_object_id),
        parameter_type_id=[
            ParameterTypeId(param.parameter_type_id) for param in request.data
        ],
    )
