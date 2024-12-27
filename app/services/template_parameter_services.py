from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.template_schemas import (
    TemplateParameterInput,
    TemplateParameterOutput,
)
from models import TemplateObject, TemplateParameter
from exceptions import (
    TemplateObjectNotFound,
    TemplateParameterNotFound,
)
from .template_services import TemplateRegistryService


class TemplateParameterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_template_object(self, template_object_id: int) -> List[TemplateParameterOutput]:
        result = await self.db.execute(
            select(TemplateObject).filter_by(
                id=template_object_id
            )
        )
        template_object = result.scalar_one_or_none()

        if not template_object:
            raise TemplateObjectNotFound

        result = await self.db.execute(
            select(TemplateParameter).filter_by(
                template_object_id=template_object_id
            )
        )
        parameters = result.scalars().all()

        return [
            TemplateParameterOutput(
                id=param.id,
                parameter_type_id=param.parameter_type_id,
                value=param.value,
                constraint=param.constraint,
                required=param.required,
                val_type=param.val_type,
                valid=param.valid,
            ) for param in parameters
        ]

    async def update_template_parameter(
        self,
        parameter_id: int,
        parameter_data: TemplateParameterInput
    ) -> TemplateParameterOutput:
        result = await self.db.execute(
            select(TemplateParameter).filter_by(id=parameter_id)
        )
        parameter = result.scalar_one_or_none()

        if not parameter:
            raise TemplateParameterNotFound

        result = await self.db.execute(
            select(TemplateObject).filter_by(id=parameter.template_object_id)
        )
        object = result.scalar_one()
        object_type_id = object.object_type_id
        
        template_registry_service = TemplateRegistryService(self.db)
        await template_registry_service.initialize_parameters_map(object_type_id)

        template_registry_service.validate_template_parameter(object_type_id, parameter_data)

        parameter.parameter_type_id = parameter_data.parameter_type_id
        parameter.value = parameter_data.value
        parameter.constraint = parameter_data.constraint
        parameter.required = parameter_data.required

        await self.db.flush()

        return TemplateParameterOutput(
            id=parameter.id,
            parameter_type_id=parameter.parameter_type_id,
            value=parameter.value,
            constraint=parameter.constraint,
            required=parameter.required,
            val_type=parameter.val_type,
            valid=parameter.valid,
        )

    async def delete_template_parameter(self, parameter_id: int) -> None:
        result = await self.db.execute(
            select(TemplateParameter).filter_by(id=parameter_id)
        )
        parameter = result.scalar_one_or_none()

        if not parameter:
            raise TemplateParameterNotFound

        await self.db.delete(parameter)

    async def commit_changes(self):
        await self.db.commit()
