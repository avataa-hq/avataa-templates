from typing import Callable, Self, Union

from typing_extensions import Any

from services.inventory_services.db_services import (
    TemplateObjectService,
    TemplateParameterService,
)
from services.inventory_services.kafka.consumer.config import (
    KafkaConfig,
)
from services.inventory_services.kafka.consumer.deserializer import (
    INVENTORY_CHANGES_HANDLER_BY_MSG_CLASS_NAME,
    INVENTORY_CHANGES_PROTOBUF_DESERIALIZERS,
    protobuf_kafka_msg_to_dict,
)
from services.inventory_services.kafka.consumer.msg_protocol import (
    KafkaMSGProtocol,
)
from services.inventory_services.kafka.consumer.protobuf import obj_pb2

KafkaMessage = Union[
    obj_pb2.ListMO, obj_pb2.ListTMO, obj_pb2.ListTPRM, obj_pb2.ListPRM
]


class InventoryChangesHandler(object):
    def __init__(self: Self, kafka_msg: KafkaMSGProtocol, key: str):
        self.msg = kafka_msg
        self.msg_instance_class_name, self.msg_instance_event = key.split(":")

    def __from_bytes_to_python_proto_model_msg(
        self,
    ) -> type[KafkaMessage]:
        if not self.msg_instance_class_name:
            raise NotImplementedError(
                f"Proto model deserializer does not implemented"
                f"for msg_class_name = '{self.msg_instance_class_name}'"
            )
        deserializer_model: Any = INVENTORY_CHANGES_PROTOBUF_DESERIALIZERS.get(
            self.msg_instance_class_name, None
        )
        if deserializer_model:
            deserializer_instance = deserializer_model()
            deserializer_instance.ParseFromString(self.msg.value())
            return deserializer_instance
        else:
            raise NotImplementedError(
                f"Proto model deserializer does not implemented"
                f"for msg_class_name = '{self.msg_instance_class_name}'"
            )

    @staticmethod
    def __deserialize_to_dict(
        deserializer_instance: type[KafkaMessage],
        including_default_value_fields: bool = True,
    ) -> dict[str, list[dict[str, str]]]:
        return protobuf_kafka_msg_to_dict(
            msg=deserializer_instance,
            including_default_value_fields=including_default_value_fields,
        )

    def __get_event_handler(self) -> Callable:
        if not self.msg_instance_class_name:
            raise NotImplementedError(
                f"Does not implemented kafka msg handlers "
                f"for the {KafkaConfig().inventory_changes_topic} topic "
                f"with msg_class_name = '{self.msg_instance_class_name}'"
            )
        handlers_by_class_name = (
            INVENTORY_CHANGES_HANDLER_BY_MSG_CLASS_NAME.get(
                self.msg_instance_class_name
            )
        )
        if not handlers_by_class_name:
            raise NotImplementedError(
                f"Does not implemented kafka msg handlers "
                f"for the {KafkaConfig().inventory_changes_topic} topic "
                f"with msg_class_name = '{self.msg_instance_class_name}'"
            )

        event_handler = handlers_by_class_name.get(self.msg_instance_event)
        if event_handler:
            return event_handler
        else:
            raise NotImplementedError(
                f"Does not implemented kafka msg handlers "
                f"for the {KafkaConfig().inventory_changes_topic} topic "
                f"with msg_class_name = '{self.msg_instance_class_name}' and "
                f"msg_event = '{self.msg_instance_event}'"
            )

    async def process_the_message(
        self,
        template_object_service: TemplateObjectService,
        template_parameter_service: TemplateParameterService,
    ):
        deserialized_msg = self.__from_bytes_to_python_proto_model_msg()

        if deserialized_msg:
            dict_msg = self.__deserialize_to_dict(
                deserializer_instance=deserialized_msg
            )
        else:
            return
        handler = self.__get_event_handler()
        await handler(
            msg=dict_msg,
            template_object_service=template_object_service,
            template_parameter_service=template_parameter_service,
        )


class InventoryChangesConverter(object):
    def __from_bytes_to_python_proto_model_msg(
        self,
    ) -> type[KafkaMessage]:
        if not self.msg_instance_class_name:
            raise NotImplementedError(
                f"Proto model deserializer does not implemented"
                f"for msg_class_name = '{self.msg_instance_class_name}'"
            )
        deserializer_model: Any = INVENTORY_CHANGES_PROTOBUF_DESERIALIZERS.get(
            self.msg_instance_class_name, None
        )
        if deserializer_model:
            deserializer_instance = deserializer_model()
            deserializer_instance.ParseFromString(self.msg.value())
            return deserializer_instance
        else:
            raise NotImplementedError(
                f"Proto model deserializer does not implemented"
                f"for msg_class_name = '{self.msg_instance_class_name}'"
            )

    @staticmethod
    def __deserialize_to_dict(
        deserializer_instance: type[KafkaMessage],
        including_default_value_fields: bool = True,
    ) -> dict[str, list[dict[str, str]]]:
        return protobuf_kafka_msg_to_dict(
            msg=deserializer_instance,
            including_default_value_fields=including_default_value_fields,
        )

    def __call__(self, msg: KafkaMSGProtocol, key: str) -> dict:
        self.msg = msg
        self.msg_instance_class_name, self.msg_instance_event = key.split(":")
        output = dict()
        deserialized_msg = self.__from_bytes_to_python_proto_model_msg()
        if deserialized_msg:
            output = self.__deserialize_to_dict(
                deserializer_instance=deserialized_msg
            )
        return output
