from logging import getLogger

from application.common.uow import UoW
from application.template_object.read.dto import TemplateObjectRequestDTO
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
    RequiredMismatchException,
    TemplateObjectNotFound,
    TPRMNotFoundInInventory,
    ValueConstraintException,
)
from application.template_parameter.create.mapper import (
    template_parameter_create_from_dto,
)
from domain.inventory_tprm.aggregate import InventoryTprmAggregate
from domain.inventory_tprm.query import TPRMReader
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import TemplateParameterCreator
from utils.constraint_validators import validate_by_constraint
from utils.val_type_validators import validate_by_val_type


class TemplateParameterCreatorInteractor(object):
    def __init__(
        self,
        tp_repo: TemplateParameterCreator,
        to_repo: TemplateObjectReader,
        inventory_tprm_repo: TPRMReader,
        uow: UoW,
    ):
        self._tp_repo = tp_repo
        self._to_repo = to_repo
        self._inventory_tprm_repo = inventory_tprm_repo
        self.uow = uow

        self.logger = getLogger("TemplateParameterCreatorInteractor")

        self.tprm_data: dict[int, dict] = dict()

    async def __call__(self, request: TemplateParameterCreateRequestDTO):
        create_dtos = list()
        # Get information about Template Object
        to_request = TemplateObjectRequestDTO(
            template_object_id=request.template_object_id,
            depth=1,
            include_parameters=False,
        )
        template_objects_filters = template_object_filter_from_dto(to_request)
        object_type_id = await self._to_repo.get_object_type_by_id(
            template_objects_filters
        )
        if not object_type_id:
            raise TemplateObjectNotFound(
                status_code=422, detail="Template object not found."
            )
        # Get information about all tprm for tmo
        self.tprm_data = (
            await self._inventory_tprm_repo.get_all_tprms_by_tmo_id(
                object_type_id
            )
        )

        for el in request.data:  # type: TemplateParameterDataCreateRequestDTO
            self._validate_template_parameter(
                tmo_id=object_type_id, parameter=el
            )
            create_dtos.append(
                template_parameter_create_from_dto(
                    dto=el,
                    template_object_id=request.template_object_id,
                    val_type=self.tprm_data[object_type_id][
                        el.parameter_type_id
                    ].val_type,
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

    def _validate_template_parameter(
        self, tmo_id: int, parameter: TemplateParameterDataCreateRequestDTO
    ):
        parameter_type_id: int = parameter.parameter_type_id
        inventory_tmo_data: dict[int, InventoryTprmAggregate] = self.tprm_data[
            tmo_id
        ]

        if parameter_type_id not in inventory_tmo_data:
            raise TPRMNotFoundInInventory(
                status_code=422,
                detail=f"Inventory tprm {parameter_type_id} not found in tmo {tmo_id}.",
            )

        if not parameter.required and parameter.required:
            raise RequiredMismatchException(
                status_code=422,
                detail=f"Inventory tprm {parameter_type_id} requires consistency error.",
            )

        if not validate_by_val_type(
            inventory_tmo_data[parameter_type_id].val_type,
            parameter.value,
            inventory_tmo_data[parameter_type_id].multiple,
        ):
            raise InvalidParameterValue(
                status_code=422,
                detail=f"Invalid value type for tprm {parameter_type_id}.",
            )
        if not validate_by_constraint(
            inventory_tmo_data[parameter_type_id].val_type,
            parameter.value,
            parameter.constraint,
            inventory_tmo_data[parameter_type_id].multiple,
        ):
            raise ValueConstraintException(
                status_code=422,
                detail=f"Invalid constraint for tprm {parameter_type_id}.",
            )
        if not validate_by_constraint(
            inventory_tmo_data[parameter_type_id].val_type,
            parameter.value,
            inventory_tmo_data[parameter_type_id].constraint,
            inventory_tmo_data[parameter_type_id].multiple,
        ):
            raise ValueConstraintException(
                status_code=422,
                detail=f"Invalid constraint for tprm {parameter_type_id}.",
            )
