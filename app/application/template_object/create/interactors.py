from logging import getLogger

from application.common.uow import UoW
from application.template_object.create.dto import (
    TemplateObjectCreateRequestDTO,
)
from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.template_object.command import TemplateObjectCreator
from domain.template_object.vo.template_object_create import (
    TemplateObjectCreate,
)


class TemplateObjectCreatorInteractor(object):
    def __init__(self, to_creator: TemplateObjectCreator, uow: UoW):
        self._to_creator = to_creator
        self._uow = uow

        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: list[TemplateObjectCreateRequestDTO]
    ) -> list:
        self.logger.info(request)
        # Create Template Object
        create_to_dtos = list()
        # create_tp_dtos = list()
        for el in request:
            create_to_dtos.append(
                TemplateObjectCreate(
                    template_id=TemplateId(el.template_id),
                    object_type_id=ObjectTypeId(el.object_type_id),
                    required=el.required,
                    valid=True,
                    parent_id=TemplateId(el.parent_id)
                    if el.parent_id
                    else None,
                )
            )
            # create_tp_dtos.append(
            #     [template_parameter_create_from_dto(
            #         dto=TemplateParameterDataCreateRequestDTO(
            #             parameter_type_id=tp.parameter_type_id,
            #             required=tp.required,
            #             value=tp.value,
            #             constraint=tp.constraint,
            #         ),
            #         template_object_id=TemplateId(el.template_id),
            #         val_type=el.val_type
            #     ) for tp in el.parameters]
            # )
        await self._to_creator.create_template_object(
            create_dtos=create_to_dtos
        )

        # Create Template Parameter
        return []
