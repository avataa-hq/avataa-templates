from enum import StrEnum
from typing import Any

from confluent_kafka import cimpl

from services.inventory_services.kafka.consumer.custom_deserializer import (
    PROTO_TYPES_SERIALIZERS,
    SerializerType,
)
from services.inventory_services.kafka.consumer.protobuf import (
    obj_pb2,
)
from services.inventory_services.kafka.events.tmo_msg import (
    on_delete_tmo,
    on_update_tmo,
)
from services.inventory_services.kafka.events.trpm_msg import (
    on_delete_tprm,
    on_update_tprm,
)


class ObjEventStatus(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


INVENTORY_CHANGES_PROTOBUF_DESERIALIZERS = {
    "MO": obj_pb2.ListMO,
    "TMO": obj_pb2.ListTMO,
    "TPRM": obj_pb2.ListTPRM,
    "PRM": obj_pb2.ListPRM,
}

TMO_HANDLERS_BY_MSG_EVENT = {
    ObjEventStatus.UPDATED.value: on_update_tmo,
    ObjEventStatus.DELETED.value: on_delete_tmo,
}

TPRM_HANDLERS_BY_MSG_EVENT = {
    ObjEventStatus.UPDATED.value: on_update_tprm,
    ObjEventStatus.DELETED.value: on_delete_tprm,
}

INVENTORY_CHANGES_HANDLER_BY_MSG_CLASS_NAME = {
    "TMO": TMO_HANDLERS_BY_MSG_EVENT,
    "TPRM": TPRM_HANDLERS_BY_MSG_EVENT,
}


def __msg_f_serializer(value: Any) -> Any:
    """Returns serialized proto msg field value into python type"""
    serializer: SerializerType | None = PROTO_TYPES_SERIALIZERS.get(
        type(value).__name__
    )
    if serializer:
        return serializer(value)
    else:
        return value


def protobuf_kafka_msg_to_dict(
    msg: cimpl.Message,
    including_default_value_fields: bool,
) -> dict[str, list[dict[str, str]]]:
    """Serialises protobuf.message.Message into python dict and returns it"""

    message_as_dict = dict()
    if including_default_value_fields is False:
        message_as_dict["objects"] = [
            {
                field.name: __msg_f_serializer(value)
                for field, value in item.ListFields()
            }
            for item in msg.objects
        ]
    else:
        message_as_dict["objects"] = [
            {
                field: __msg_f_serializer(getattr(item, field))
                for field in item.DESCRIPTOR.fields_by_name.keys()
            }
            for item in msg.objects
        ]
    return message_as_dict
