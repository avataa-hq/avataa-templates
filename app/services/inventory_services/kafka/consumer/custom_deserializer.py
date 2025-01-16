from typing import Any, Callable, TypeVar, Union

from google.protobuf import json_format
from google.protobuf.internal.containers import (
    RepeatedScalarFieldContainer,
)
from google.protobuf.internal.well_known_types import (
    Struct,
    Timestamp,
)

T = TypeVar("T")
SerializerType = Callable[
    [Any], Union[dict, str, list, Any]
]


def from_struct_to_dict(value: Struct):
    """Converts Struct to python dict and returns it"""
    return json_format.MessageToDict(value)


def from_proto_timestamp_to_dict(
    value: Timestamp,
):
    """Converts proto Timestamp to python str and returns it"""
    return json_format.MessageToDict(value).split(
        "Z"
    )[0]


def from_repeated_scalar_field_container_to_list(
    value: RepeatedScalarFieldContainer,
):
    """Converts proto Timestamp to python str and returns it"""
    return list(value)


PROTO_TYPES_SERIALIZERS: dict[
    str, SerializerType
] = {
    "Struct": from_struct_to_dict,
    "Timestamp": from_proto_timestamp_to_dict,
    "RepeatedScalarFieldContainer": from_repeated_scalar_field_container_to_list,
    "RepeatedScalarContainer": from_repeated_scalar_field_container_to_list,
}
