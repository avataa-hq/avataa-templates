from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from exceptions import (
    TemplateNotFound,
    TemplateObjectNotFound,
)
from models import Template, TemplateObject
from schemas.template_schemas import (
    TemplateObjectOutput,
    TemplateObjectUpdateInput,
    TemplateObjectUpdateOutput,
    TemplateParameterOutput,
)

from .template_services import (
    TemplateRegistryService,
)


class TemplateObjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_template_objects(
        self,
        template_id: int,
        parent_id: int | None = None,
        include_parameters: bool = False,
        depth: int = 1,
    ) -> list[TemplateObjectOutput]:
        if depth <= 0:
            return []

        result = await self.db.execute(
            select(Template).filter_by(id=template_id)
        )
        template = result.scalar_one_or_none()
        if not template:
            raise TemplateNotFound

        query = select(TemplateObject).filter(
            TemplateObject.template_id == template_id
        )

        if parent_id:
            result = await self.db.execute(
                select(TemplateObject).filter(
                    TemplateObject.id == parent_id,
                    TemplateObject.template_id == template_id,
                )
            )
            parent_template_object = result.scalar_one_or_none()
            if not parent_template_object:
                raise TemplateObjectNotFound

            query = query.filter(TemplateObject.parent_object_id == parent_id)
        else:
            query = query.filter(TemplateObject.parent_object_id.is_(None))

        if include_parameters:
            query = query.options(selectinload(TemplateObject.parameters))

        result = await self.db.execute(query)
        template_objects = result.scalars().all()

        objects: list[TemplateObjectOutput] = list()

        for obj in template_objects:
            # Include parameters if flag is True
            parameters = list()
            if include_parameters:
                parameters = [
                    TemplateParameterOutput(
                        id=param.id,
                        parameter_type_id=param.parameter_type_id,
                        value=param.value,
                        constraint=param.constraint,
                        required=param.required,
                        val_type=param.val_type,
                        valid=param.valid,
                    )
                    for param in obj.parameters
                ]

            # Recursively fetch children
            children = await self.get_template_objects(
                template_id=template_id,
                parent_id=obj.id,
                depth=depth - 1,
                include_parameters=include_parameters,
            )

            objects.append(
                TemplateObjectOutput(
                    id=obj.id,
                    object_type_id=obj.object_type_id,
                    required=obj.required,
                    parameters=parameters,
                    children=children,
                    valid=obj.valid,
                )
            )

        return objects

    async def update_template_object(
        self,
        object_id: int,
        object_data: TemplateObjectUpdateInput,
    ) -> TemplateObjectUpdateOutput:
        result = await self.db.execute(
            select(TemplateObject).filter_by(id=object_id)
        )
        object = result.scalar_one_or_none()

        if not object:
            raise TemplateObjectNotFound

        if (
            object_data.parent_object_id
            and object_data.parent_object_id != object.parent_object_id
        ):
            # if hierarchy is changing
            registry_service = TemplateRegistryService(self.db)
            await registry_service.initialize_hierarchy_map()
            parent_id: int | None = object_data.parent_object_id
            parent_object_type_id: int | None = None

            result = await self.db.execute(
                select(TemplateObject).filter_by(id=parent_id)
            )
            parent_object = result.scalar_one_or_none()
            if not parent_object:
                raise TemplateObjectNotFound(
                    f"Parent object with id {parent_id} not found"
                )

            parent_object_type_id = parent_object.object_type_id

            registry_service.validate_object_type(
                object_type_id=object.object_type_id,
                parent_object_type_id=parent_object_type_id,
            )

        object.parent_object_id = object_data.parent_object_id
        object.required = object_data.required

        await self.db.flush()

        return TemplateObjectUpdateOutput(
            id=object.id,
            object_type_id=object.object_type_id,
            parent_object_id=object.parent_object_id,
            required=object.required,
            valid=object.valid,
        )

    async def delete_template_object(self, object_id: int) -> None:
        result = await self.db.execute(
            select(TemplateObject).filter_by(id=object_id)
        )
        object = result.scalar_one_or_none()

        if not object:
            raise TemplateObjectNotFound

        await self.db.delete(object)

    async def commit_changes(self) -> None:
        await self.db.commit()
