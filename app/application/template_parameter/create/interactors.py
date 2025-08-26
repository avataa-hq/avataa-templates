from logging import getLogger

from application.common.uow import UoW
from application.paramater_validation.interactors import (
    ParameterValidationInteractor,
)
from application.template_object.read.dto import TemplateObjectRequestDTO
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from application.template_object.read.mapper import (
    template_object_filter_from_dto,
)
from application.template_parameter.create.dto import (
    TemplateParameterCreatedDTO,
    TemplateParameterCreateRequestDTO,
    TemplateParameterDataCreateRequestDTO,
)
from application.template_parameter.create.exceptions import (
    InvalidParameterValue,
    TemplateObjectNotFound,
)
from application.template_parameter.create.mapper import (
    template_parameter_create_from_dto,
    template_parameter_to_validator,
)
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import TemplateParameterCreator


class TemplateParameterCreatorInteractor(object):
    def __init__(
        self,
        tp_repo: TemplateParameterCreator,
        to_repo: TemplateObjectReader,
        tprm_validator: ParameterValidationInteractor,
        uow: UoW,
    ):
        self._tp_repo = tp_repo
        self._to_repo = to_repo
        self._tprm_validator = tprm_validator
        self.uow = uow

        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: TemplateParameterCreateRequestDTO
    ) -> list[TemplateParameterCreatedDTO]:
        create_dtos = list()
        # Get information about Template Object
        to_request = TemplateObjectRequestDTO(
            template_object_id=request.template_object_id,
            depth=1,
            include_parameters=False,
        )
        template_objects_filters = template_object_filter_from_dto(to_request)
        try:
            object_type_id = await self._to_repo.get_object_type_by_id(
                template_objects_filters
            )
        except TemplateObjectReaderApplicationException as ex:
            raise TemplateObjectNotFound(
                status_code=ex.status_code,
                detail=ex.detail,
            )
        # Get information about all tprm for tmo
        inventory_request = template_parameter_to_validator(
            object_type_id, request.data
        )
        validated_data = await self._tprm_validator(request=inventory_request)
        if validated_data.invalid_items:
            raise InvalidParameterValue(
                status_code=422, detail=" ".join(validated_data.errors)
            )
        for el in validated_data.valid_items:
            create_dtos.append(
                template_parameter_create_from_dto(
                    dto=TemplateParameterDataCreateRequestDTO(
                        parameter_type_id=el.parameter_type_id,
                        required=el.required,
                        value=el.value,
                        constraint=el.constraint,
                    ),
                    template_object_id=request.template_object_id,
                    val_type=el.val_type,
                )
            )
        created_parameters = await self._tp_repo.create_template_parameters(
            create_dtos=create_dtos
        )
        await self.uow.commit()
        # Create user response
        result = [
            TemplateParameterCreatedDTO.from_aggregate(created)
            for created in created_parameters
        ]
        return result
