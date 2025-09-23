from logging import getLogger

from application.tprm_validation.dto import (
    TemplateParameterValidationDTO,
    TemplateParameterValidationRequestDTO,
    TemplateParameterValidationResponseDTO,
    TemplateParameterWithTPRMData,
)
from application.tprm_validation.exceptions import (
    ParameterValidationException,
)
from domain.tprm_validation.aggregate import InventoryTprmAggregate
from domain.tprm_validation.query import TPRMReader
from domain.tprm_validation.vo.validation_filter import (
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
        # Generate filters
        repo_filter = ParameterValidationFilter(tmo_id=request.object_type_id)
        # gRPC request
        result = await self._repository.get_all_tprms_by_tmo_id(repo_filter)
        # Check correct data
        request_list_of_parameters = [
            p.parameter_type_id for p in request.parameter_to_validate
        ]
        if not set(request_list_of_parameters).issubset(result.keys()):
            raise ParameterValidationException(
                status_code=422,
                detail=f"Inconsistent request parameters: {request_list_of_parameters}"
                f" do not belong tmo {repo_filter.tmo_id}.",
            )
        #  Check user data
        valid_params, invalid_params, errors = self.check_user_data(
            request.parameter_to_validate, result
        )

        # Generate results
        return TemplateParameterValidationResponseDTO(
            valid_items=valid_params,
            invalid_items=invalid_params,
            errors=errors,
        )

    @staticmethod
    def check_user_data(
        params_to_validate: list[TemplateParameterValidationDTO],
        result: dict[int, InventoryTprmAggregate],
    ) -> tuple[
        list[TemplateParameterWithTPRMData],
        list[TemplateParameterWithTPRMData],
        list[str],
    ]:
        valid_parameters: list[TemplateParameterWithTPRMData] = []
        invalid_parameters: list[TemplateParameterWithTPRMData] = []
        errors: list[str] = []
        for el in params_to_validate:
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
        return valid_parameters, invalid_parameters, errors
