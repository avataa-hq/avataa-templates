from typing import Optional


class TemplateNotFound(Exception):
    pass


class TemplateObjectNotFound(Exception):
    pass


class TemplateParameterNotFound(Exception):
    pass


class TMOIdNotFoundInInventory(Exception):
    def __init__(self, object_type_id: int) -> None:
        self.object_type_id = object_type_id
        super().__init__(f"TMO id {object_type_id} not found in inventory.")


class TPRMNotFoundInInventory(Exception):
    def __init__(
        self,
        parameter_type_id: int,
        object_type_id: int,
    ) -> None:
        self.parameter_type_id = parameter_type_id
        self.object_type_id = object_type_id
        super().__init__(
            f"Parameter type ID {parameter_type_id} not found for object type ID {object_type_id}."
        )


class InvalidHierarchy(Exception):
    def __init__(
        self,
        object_type_id: int,
        expected_parent_id: Optional[int],
        actual_parent_id: Optional[int],
    ) -> None:
        self.object_type_id = object_type_id
        self.expected_parent_id = expected_parent_id
        self.actual_parent_id = actual_parent_id
        super().__init__(
            f"Hierarchy error: object_type_id {object_type_id} "
            f"expected parent {expected_parent_id}, got {actual_parent_id}."
        )


class RequiredMismatchException(Exception):
    def __init__(
        self,
        parameter_type_id: int,
        object_type_id: int,
    ) -> None:
        self.parameter_type_id = parameter_type_id
        self.object_type_id = object_type_id
        super().__init__(
            f"Required mismatch for parameter type ID {parameter_type_id} (object type ID {object_type_id}): "
            f"expected `required=True`, but got `required=False`."
        )


class InvalidParameterValue(Exception):
    def __init__(
        self,
        parameter_type_id: int,
        object_type_id: int,
        tprm_val_type: str,
        tprm_is_multiple: bool,
        value: str,
    ) -> None:
        # self.parameter_type_id = parameter_type_id
        # self.object_type_id = object_type_id
        # self.value = value
        super().__init__(
            f"Invalid value '{value}' for parameter type (ID={parameter_type_id}, "
            f"type={tprm_val_type}, is_multiple={tprm_is_multiple}) "
            f"in object type (ID={object_type_id})."
        )


class ValueConstraintException(Exception):
    def __init__(
        self,
        parameter_type_id: int,
        object_type_id: int,
        value: str,
        constraint: str,
        tprm_val_type: str,
        tprm_is_multiple: bool,
    ) -> None:
        super().__init__(
            f"Constraint validation failed for value `{value}` for parameter type "
            f"(ID={parameter_type_id}, type={tprm_val_type}, is_multiple={tprm_is_multiple} , "
            f"constraint=`{constraint}`) in object type (ID={object_type_id})"
        )


class IncorrectConstraintException(Exception):
    def __init__(
        self,
        constraint: str,
    ) -> None:
        super().__init__(f"Constraint was defined incorrectly: `{constraint}`")
