def cast_to_str(value: str) -> str:
    return value


def cast_to_int(value: str) -> int:
    return int(value)


def cast_to_float(value: str) -> float:
    return float(value)


def cast_to_bool(value: str) -> bool:
    if value.lower() in ("true", "1"):
        return True
    elif value.lower() in ("false", "0"):
        return False
    raise ValueError(f"Cannot cast '{value}' to a boolean.")


param_type_casting_router = {
    "str": cast_to_str,
    "user_link": cast_to_str,
    "bool": cast_to_bool,
    "int": cast_to_int,
    "float": cast_to_float,
    "formula": cast_to_float,
    "date": cast_to_str,  # Date and datetime remain strings for validation
    "datetime": cast_to_str,
    "mo_link": cast_to_int,
    "prm_link": cast_to_int,
    "sequence": cast_to_int,
}
