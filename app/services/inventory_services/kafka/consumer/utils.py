from typing import Callable, Self

from confluent_kafka import cimpl
from typing_extensions import Any

from services.inventory_services.db_services import (
    TemplateObjectService,
    TemplateParameterService,
)
from services.inventory_services.kafka.consumer.config import (
    KafkaConfig,
)
from services.inventory_services.kafka.consumer.deserializer import (
    INVENTORY_CHANGES_PROTOBUF_DESERIALIZERS,
    protobuf_kafka_msg_to_dict,
    INVENTORY_CHANGES_HANDLER_BY_MSG_CLASS_NAME,
)
from services.inventory_services.kafka.consumer.msg_protocol import (
    KafkaMSGProtocol,
)


class InventoryChangesHandler(object):
    def __init__(self, kafka_msg: KafkaMSGProtocol):
        self.msg = kafka_msg
        self.msg_instance_class_name = None
        self.msg_instance_event = None
        self.allowed_msg_class_name = [
            "TMO",
            "TPRM",
        ]
        self.allowed_msg_event = [
            "deleted",
            "updated",
        ]

    def clear_msg_data(self: Self) -> None:
        """Clears the message data, if successful, change self.msg_instance_class_name and self.msg_instance_event,
        otherwise self.msg_instance_class_name and self.msg_instance_event will be None
        """
        msg_key = getattr(self.msg, "key", None)
        if msg_key is None:
            return

        msg_key = msg_key()
        if msg_key is None:
            return

        # msg_key in this case must be bytes
        msg_key = msg_key.decode("utf-8")
        if msg_key.find(":") == -1:
            return

        msg_class_name, msg_event = msg_key.split(":")
        if (
            msg_class_name
            and msg_event
            and msg_class_name in self.allowed_msg_class_name
            and msg_event in self.allowed_msg_event
        ):
            self.msg_instance_class_name = msg_class_name
            self.msg_instance_event = msg_event

    def __from_bytes_to_python_proto_model_msg(
        self,
    ) -> cimpl.Message:
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
        deserializer_instance: cimpl.Message,
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
        self.clear_msg_data()
        if self.msg_instance_class_name:
            deserialized_msg = self.__from_bytes_to_python_proto_model_msg()

            if deserialized_msg:
                deserialized_msg = self.__deserialize_to_dict(
                    deserializer_instance=deserialized_msg
                )
            else:
                return
            handler = self.__get_event_handler()
            await handler(
                msg=deserialized_msg,
                template_object_service=template_object_service,
                template_parameter_service=template_parameter_service,
            )
