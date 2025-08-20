import ast
from datetime import datetime
import json
from typing import Callable


def str_validation(value: str) -> bool:
    return True


def int_validation(value: str) -> bool:
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def float_validation(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def bool_validation(value: str) -> bool:
    if value.lower() in (
        "true",
        "1",
        "false",
        "0",
    ):
        return True
    return False


def date_validation(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except Exception:
        return False


def datetime_validation(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True
    except Exception:
        return False


def mo_link_validation(value: str) -> bool:
    if not value.isdigit():
        return False
    return True


def prm_link_validation(value: str) -> bool:
    if not value.isdigit():
        return False
    return True


def sequence_validation(value: str) -> bool:
    if not value.isdigit():
        return False
    return True


param_validation_by_val_type_router = {
    "str": str_validation,
    "user_link": str_validation,
    "bool": bool_validation,
    "int": int_validation,
    "float": float_validation,
    "formula": float_validation,
    "date": date_validation,
    "datetime": datetime_validation,
    "mo_link": mo_link_validation,
    "prm_link": prm_link_validation,
    "sequence": sequence_validation,
    "enum": str_validation,
}


def parse_maybe_list(value: str) -> list | None:
    try:
        result = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        try:
            result = json.loads(value)
        except json.JSONDecodeError:
            return None
    return result if isinstance(result, list) else None


def validate_by_val_type(
    val_type: str,
    value: str | None,
    is_multiple: bool = False,
) -> bool:
    """
    Validates a single or multiple values based on the val_type.

    Args:
        val_type (str): The type of the value (e.g., 'int', 'float').
        value (str): The value to validate.
        is_multiple (bool): Whether the value is a list of items.

    Returns:
        bool: True if the value(s) are valid; False otherwise.
    """
    validator_function: Callable | None = (
        param_validation_by_val_type_router.get(val_type)
    )

    if not validator_function or not value:
        return True

    if is_multiple:
        value_list = parse_maybe_list(value)
        if value_list is None:
            return False

        return all(validator_function(str(item)) for item in value_list)

    return validator_function(value)
