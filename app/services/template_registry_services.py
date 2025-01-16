from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.template_schemas import (
    TemplateInput,
    TemplateOutput,
    TemplateObjectInput,
    TemplateObjectOutput,
    TemplateParameterInput,
    TemplateParameterOutput,
)
from grpc_clients.inventory.getters.getters_with_channel import (
    get_all_tmo_data_from_inventory_channel_in,
    get_all_tprms_for_special_tmo_id_channel_in,
)
from utils.val_type_validators import (
    validate_by_val_type,
)
from utils.constraint_validators import (
    validate_by_constraint,
)
from models import (
    Template,
    TemplateObject,
    TemplateParameter,
)
from exceptions import (
    TemplateNotFound,
    TemplateObjectNotFound,
    TMOIdNotFoundInInventory,
    TPRMNotFoundInInventory,
    InvalidHierarchy,
    RequiredMismatchException,
    InvalidParameterValue,
    ValueConstraintException,
)


class TemplateRegistryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.object_type_to_parent: Dict[
            int, Optional[int]
        ] = dict()
        self.object_type_to_parameter: Dict[
            int, Dict
        ] = dict()

    async def initialize_hierarchy_map(
        self,
    ) -> None:
        all_tmo_data = await get_all_tmo_data_from_inventory_channel_in()
        self.object_type_to_parent = {
            item["id"]: item["p_id"]
            for item in all_tmo_data
            if "id" in item and "p_id" in item
        }

    async def initialize_parameters_map(
        self, tmo_id: int
    ) -> None:
        if (
            tmo_id
            not in self.object_type_to_parameter
        ):
            all_tprms = await get_all_tprms_for_special_tmo_id_channel_in(
                tmo_id
            )

            self.object_type_to_parameter[
                tmo_id
            ] = dict()
            for param in all_tprms:
                param_dict = {
                    "val_type": param["val_type"],
                    "constraint": param[
                        "constraint"
                    ],
                    "required": param["required"],
                    "multiple": param["multiple"],
                }
                self.object_type_to_parameter[
                    tmo_id
                ][param["id"]] = param_dict

    def validate_object_type(
        self,
        object_type_id: int,
        parent_object_type_id: Optional[
            int
        ] = None,
    ) -> None:
        if (
            object_type_id
            not in self.object_type_to_parent
        ):
            raise TMOIdNotFoundInInventory(
                object_type_id
            )

        if parent_object_type_id is not None:
            expected_parent_id = (
                self.object_type_to_parent.get(
                    object_type_id
                )
            )
            if (
                expected_parent_id
                != parent_object_type_id
            ):
                raise InvalidHierarchy(
                    object_type_id=object_type_id,
                    expected_parent_id=expected_parent_id,
                    actual_parent_id=parent_object_type_id,
                )

    def validate_template_parameter(
        self,
        object_type_id: int,
        template_parameter: TemplateParameterInput,
    ) -> None:
        parameter_type_id: int = (
            template_parameter.parameter_type_id
        )
        inventory_tmo_data = (
            self.object_type_to_parameter[
                object_type_id
            ]
        )

        if (
            parameter_type_id
            not in inventory_tmo_data
        ):
            raise TPRMNotFoundInInventory(
                parameter_type_id, object_type_id
            )

        inventory_tprm_data = inventory_tmo_data[
            parameter_type_id
        ]
        inventory_val_type = inventory_tprm_data[
            "val_type"
        ]
        inventory_is_multiple = (
            inventory_tprm_data["multiple"]
        )
        inventory_constraint = (
            inventory_tprm_data["constraint"]
        )

        if (
            not template_parameter.required
            and inventory_tprm_data["required"]
        ):
            raise RequiredMismatchException(
                parameter_type_id,
                object_type_id,
            )

        template_value = template_parameter.value
        template_constraint = (
            template_parameter.constraint
        )

        if not validate_by_val_type(
            inventory_val_type,
            template_value,
            inventory_is_multiple,
        ):
            raise InvalidParameterValue(
                parameter_type_id=parameter_type_id,
                object_type_id=object_type_id,
                tprm_val_type=inventory_val_type,
                tprm_is_multiple=inventory_is_multiple,
                value=template_value,
            )

        if not validate_by_constraint(
            inventory_val_type,
            template_value,
            template_constraint,
            inventory_is_multiple,
        ):
            raise ValueConstraintException(
                parameter_type_id=parameter_type_id,
                object_type_id=object_type_id,
                tprm_val_type=inventory_val_type,
                tprm_is_multiple=inventory_is_multiple,
                value=template_value,
                constraint=template_constraint,
            )

        if not validate_by_constraint(
            inventory_val_type,
            template_value,
            inventory_constraint,
            inventory_is_multiple,
        ):
            raise ValueConstraintException(
                parameter_type_id=parameter_type_id,
                object_type_id=object_type_id,
                tprm_val_type=inventory_val_type,
                tprm_is_multiple=inventory_is_multiple,
                value=template_value,
                constraint=inventory_constraint,
            )

    async def create_template(
        self, template_data: TemplateInput
    ) -> TemplateOutput:
        if not self.object_type_to_parent:
            await self.initialize_hierarchy_map()

        self.validate_object_type(
            template_data.object_type_id
        )

        db_template = Template(
            name=template_data.name,
            owner=template_data.owner,
            object_type_id=template_data.object_type_id,
        )
        self.db.add(db_template)
        await self.db.flush()
        await self.db.refresh(db_template)

        created_objects = (
            await self.create_template_objects(
                template_data.template_objects,
                template_id=db_template.id,
            )
        )

        return TemplateOutput(
            id=db_template.id,
            name=db_template.name,
            owner=db_template.owner,
            object_type_id=db_template.object_type_id,
            template_objects=created_objects,
            valid=db_template.valid,
        )

    async def create_template_objects(
        self,
        template_objects_data: Optional[
            List[TemplateObjectInput]
        ],
        template_id: int,
        parent_id: Optional[int] = None,
        parent_object_type_id: Optional[
            int
        ] = None,
    ) -> List[TemplateObjectOutput]:
        if not template_objects_data:
            return []

        if (
            parent_id
            and not parent_object_type_id
        ):
            parent_template_object = await self.get_template_object_or_raise(
                parent_id
            )
            parent_object_type_id = parent_template_object.object_type_id

        if not self.object_type_to_parent:
            await self.initialize_hierarchy_map()

        created_objects = list()

        for (
            template_object_data
        ) in template_objects_data:
            self.validate_object_type(
                object_type_id=template_object_data.object_type_id,
                parent_object_type_id=parent_object_type_id,
            )

            db_template_object = TemplateObject(
                object_type_id=template_object_data.object_type_id,
                required=template_object_data.required,
                template_id=template_id,
                parent_object_id=parent_id,
            )
            self.db.add(db_template_object)
            await self.db.flush()
            await self.db.refresh(
                db_template_object
            )

            parameters = await self.create_template_parameters(
                template_object_data.parameters,
                db_template_object.id,
                db_template_object.object_type_id,
            )

            children = await self.create_template_objects(
                template_object_data.children,
                template_id=template_id,
                parent_id=db_template_object.id,
                parent_object_type_id=template_object_data.object_type_id,
            )

            created_objects.append(
                TemplateObjectOutput(
                    id=db_template_object.id,
                    object_type_id=db_template_object.object_type_id,
                    required=db_template_object.required,
                    parameters=parameters,
                    children=children,
                    valid=db_template_object.valid,
                )
            )

        return created_objects

    async def create_template_parameters(
        self,
        parameters_data: Optional[
            List[TemplateParameterInput]
        ],
        template_object_id: int,
        object_type_id: Optional[int] = None,
    ) -> List[TemplateParameterOutput]:
        if not object_type_id:
            template_object = await self.get_template_object_or_raise(
                template_object_id
            )
            object_type_id = (
                template_object.object_type_id
            )

        await self.initialize_parameters_map(
            object_type_id
        )

        if not parameters_data:
            return []

        parameters = list()
        for parameter in parameters_data:
            self.validate_template_parameter(
                object_type_id=object_type_id,
                template_parameter=parameter,
            )

            inventory_tprm_data = (
                self.object_type_to_parameter[
                    object_type_id
                ]
            )
            val_type = inventory_tprm_data[
                parameter.parameter_type_id
            ]["val_type"]

            db_parameter = TemplateParameter(
                parameter_type_id=parameter.parameter_type_id,
                value=parameter.value,
                constraint=parameter.constraint,
                required=parameter.required,
                template_object_id=template_object_id,
                val_type=val_type,
            )
            self.db.add(db_parameter)
            await self.db.flush()
            await self.db.refresh(db_parameter)

            parameters.append(
                TemplateParameterOutput(
                    **db_parameter.__dict__
                )
            )
        return parameters

    async def get_template_or_raise(
        self, template_id: int
    ) -> Template:
        result = await self.db.execute(
            select(Template).filter_by(
                id=template_id
            )
        )
        template = result.scalar_one_or_none()
        if not template:
            raise TemplateNotFound
        return template

    async def get_template_object_or_raise(
        self, template_object_id: int
    ) -> TemplateObject:
        result = await self.db.execute(
            select(TemplateObject).filter_by(
                id=template_object_id
            )
        )
        template_object = (
            result.scalar_one_or_none()
        )
        if not template_object:
            raise TemplateObjectNotFound
        return template_object

    async def commit_changes(self):
        await self.db.commit()
