import ast
import re
from typing import Any, Optional, Callable
from .type_casting_functions import (
    param_type_casting_router,
)
from exceptions import (
    IncorrectConstraintException,
)


def str_value_constraint_validation(
    value: str, constraint: str
) -> bool:
    pattern = re.compile(rf"{constraint}")
    if pattern.match(value):
        return True
    return False


def non_value_constraint_validation(
    value: Any, constraint: Any
) -> bool:
    """Always correct"""
    return True


def float_value_constraint_validation(
    value: float, constraint: str
) -> bool:
    bottom, top = constraint.split(":")
    top = float(top)
    bottom = float(bottom)

    return bottom < value < top


def int_value_constraint_validation(
    value: int, constraint: str
) -> bool:
    bottom, top = constraint.split(":")
    top = int(top)
    bottom = int(bottom)

    return bottom < value < top


param_value_constraint_validation_router = {
    "str": str_value_constraint_validation,
    "date": non_value_constraint_validation,
    "datetime": non_value_constraint_validation,
    "float": float_value_constraint_validation,
    "int": int_value_constraint_validation,
    "bool": non_value_constraint_validation,
    "user_link": str_value_constraint_validation,
    "formula": non_value_constraint_validation,
    "mo_link": non_value_constraint_validation,
    "prm_link": non_value_constraint_validation,
    "sequence": non_value_constraint_validation,
}


def validate_by_constraint(
    val_type: str,
    value: Optional[str],
    constraint: Optional[str],
    is_multiple: bool = False,
) -> bool:
    """
    Validates a single or multiple values based on the val_type and constraint.

    Args:
        val_type (str): The type of the value (e.g., 'int', 'float').
        value (Optional[str]): The value to validate.
        constraint (Optional[str]): The constraint to apply (e.g., a range or regex).
        is_multiple (bool): Whether the value represents a list of items.

    Returns:
        bool: True if the value(s) are valid; False otherwise.

    I suppose that `value` correctly correlates with `value_type`.
    """
    cast_function: Optional[Callable] = (
        param_type_casting_router.get(val_type)
    )
    validator_function: Optional[Callable] = (
        param_value_constraint_validation_router.get(
            val_type
        )
    )

    if (
        validator_function
        == non_value_constraint_validation
    ):
        return True

    if (
        not cast_function
        or not validator_function
        or not value
        or not constraint
    ):
        return True

    try:
        if is_multiple:
            value_list = ast.literal_eval(value)
            return all(
                validator_function(
                    cast_function(item),
                    constraint,
                )
                for item in value_list
            )

        return validator_function(
            cast_function(value), constraint
        )
    except ValueError:
        raise IncorrectConstraintException(
            constraint
        )
