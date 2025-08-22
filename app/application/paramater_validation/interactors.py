from logging import getLogger

from application.paramater_validation.dto import (
    TemplateParameterValidationRequestDTO,
    TemplateParameterValidationResponseDTO,
    TemplateParameterWithTPRMData,
)
from domain.parameter_validation.query import TPRMReader
from domain.parameter_validation.vo.validation_filter import (
    ParameterValidationFilter,
)
from utils.constraint_validators import validate_by_constraint
from utils.val_type_validators import validate_by_val_type


class ParameterValidationInteractor(object):
    def __init__(self, repository: TPRMReader):
        self._repository = repository
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterValidationRequestDTO
    ) -> TemplateParameterValidationResponseDTO:
        valid_parameters: list[TemplateParameterWithTPRMData] = []
        invalid_parameters: list[TemplateParameterWithTPRMData] = []
        errors: list[str] = []
        # Generate filters
        repo_filter = ParameterValidationFilter(tmo_id=request.object_type_id)
        # gRPC request
        result = await self._repository.get_all_tprms_by_tmo_id(repo_filter)
        #  Check user data
        for el in request.parameter_to_validate:
            parameter_type_id: int = el.parameter_type_id
            if not validate_by_val_type(
                result[parameter_type_id].val_type,
                el.value,
                result[parameter_type_id].multiple,
            ):
                invalid_parameters.append(
                    TemplateParameterWithTPRMData(
                        parameter_type_id=parameter_type_id,
                        required=el.required,
                        val_type=result[parameter_type_id].val_type,
                        multiple=result[parameter_type_id].multiple,
                        value=el.value,
                        constraint=el.constraint,
                    )
                )
                errors.append(
                    f"Invalid value type for tprm {parameter_type_id}."
                )
                continue
            if not validate_by_constraint(
                result[parameter_type_id].val_type,
                el.value,
                el.constraint,
                result[parameter_type_id].multiple,
            ):
                invalid_parameters.append(
                    TemplateParameterWithTPRMData(
                        parameter_type_id=parameter_type_id,
                        required=el.required,
                        val_type=result[parameter_type_id].val_type,
                        multiple=result[parameter_type_id].multiple,
                        value=el.value,
                        constraint=el.constraint,
                    )
                )
                errors.append(
                    f"Invalid constraint for tprm {parameter_type_id}."
                )
                continue
            if not validate_by_constraint(
                result[parameter_type_id].val_type,
                el.value,
                result[parameter_type_id].constraint,
                result[parameter_type_id].multiple,
            ):
                invalid_parameters.append(
                    TemplateParameterWithTPRMData(
                        parameter_type_id=parameter_type_id,
                        required=el.required,
                        val_type=result[parameter_type_id].val_type,
                        multiple=result[parameter_type_id].multiple,
                        value=el.value,
                        constraint=el.constraint,
                    )
                )
                errors.append(
                    f"Invalid constraint for tprm {parameter_type_id}."
                )
                continue
            valid_parameters.append(
                TemplateParameterWithTPRMData(
                    parameter_type_id=parameter_type_id,
                    required=el.required,
                    val_type=result[parameter_type_id].val_type,
                    multiple=result[parameter_type_id].multiple,
                    value=el.value,
                    constraint=el.constraint,
                )
            )

        # Generate results
        return TemplateParameterValidationResponseDTO(
            valid_items=valid_parameters,
            invalid_items=invalid_parameters,
            errors=errors,
        )
