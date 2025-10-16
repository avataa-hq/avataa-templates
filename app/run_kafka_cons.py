import asyncio
import functools
from time import sleep
from typing import Any, Union

from confluent_kafka import (
    Consumer,
    KafkaException,
    Message,
    TopicPartition,
)
from confluent_kafka.admin import TopicMetadata
from dishka import make_async_container

from application.inventory_changes.interactors import InventoryChangesInteractor
from infrastructure.di.providers import (
    DatabaseProvider,
    InteractorProvider,
    KafkaProvider,
    KafkaServiceProvider,
    RepositoryProvider,
)
from services.inventory_services.kafka.consumer.config import (
    KafkaConfig,
)
from services.inventory_services.kafka.consumer.custom_deserializer import (
    PROTO_TYPES_SERIALIZERS,
    SerializerType,
)
from services.inventory_services.kafka.consumer.protobuf import obj_pb2

KafkaMessage = Union[obj_pb2.ListTMO, obj_pb2.ListTPRM]


async def initialize_kafka_consumer(consumer: Consumer) -> bool:
    config = KafkaConfig()
    try:
        print(f"Subscribing to topic: {config.inventory_changes_topic}")

        consumer.subscribe(
            [config.inventory_changes_topic],
            on_assign=on_assign,
            on_revoke=on_revoke,
            on_lost=on_lost,
        )

        print("Successfully subscribed to Kafka topic")
        print("Testing Kafka connection...")
        test_msg = consumer.poll(timeout=3.0)
        if test_msg is not None and test_msg.error():
            print(f"Kafka warning: {test_msg.error()}")
        else:
            print("Kafka connection established")
        return True

    except Exception as ex:
        print(f"Failed to subscribe to Kafka topic: {ex}")
        print(f"Topic: {config.inventory_changes_topic}")
        print(f"Brokers: {config.bootstrap_servers}")
        print(f"Group ID: {config.group_id}")
        return False


async def run_kafka_cons_inv() -> None:
    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        InteractorProvider(),
        KafkaProvider(),
        KafkaServiceProvider(),
    )
    message_batch: list[tuple[dict, str, str]] = []
    batch_size = 100
    loop = asyncio.get_running_loop()
    async with container() as di:
        consumer = await di.get(Consumer)
        interactor = await di.get(InventoryChangesInteractor)
        if not await initialize_kafka_consumer(consumer):
            print("Failed to initialize Kafka consumer. Exiting...")
            return
        try:
            while True:
                poll = functools.partial(consumer.poll, 1.0)
                msg = await loop.run_in_executor(None, poll)

                if msg is None:
                    if message_batch:
                        await interactor(message_batch)
                        message_batch.clear()
                    continue
                if not msg.key():
                    consumer.commit(asynchronous=True)
                    continue
                entity_type, operation = parse_key_message(msg.key())
                if not is_relevant_message_type(entity_type, operation):
                    consumer.commit(asynchronous=True)
                    continue
                message_batch.append(
                    (deserialize_msg(msg, entity_type), entity_type, operation)
                )
                if len(message_batch) >= batch_size:
                    await interactor(message_batch)
                    message_batch.clear()
                consumer.commit(asynchronous=False)
        except (KeyboardInterrupt, asyncio.CancelledError):
            if message_batch:
                await interactor(message_batch)
                # send dead letter
                print("Error processing final batch")
                message_batch.clear()
            print("Kafka consumer - end")


def deserialize_msg(msg: Message, key) -> dict:
    deserializer = {
        "TMO": obj_pb2.ListTMO,
        "TPRM": obj_pb2.ListTPRM,
    }
    result = {}
    deserializer_model = deserializer.get(key, None)
    if deserializer_model:
        deserializer_instance = deserializer_model()
        deserializer_instance.ParseFromString(msg.value())
        result["objects"] = [
            {
                field: __msg_f_serializer(getattr(item, field))
                for field in item.DESCRIPTOR.fields_by_name.keys()
            }
            for item in deserializer_instance.objects
        ]

    return result


def __msg_f_serializer(value: Any) -> Any:
    """Returns serialized proto msg field value into python type"""
    serializer: SerializerType | None = PROTO_TYPES_SERIALIZERS.get(
        type(value).__name__
    )
    if serializer:
        return serializer(value)
    else:
        return value


def on_assign(consumer: Consumer, partitions: list[TopicPartition]) -> None:
    cons_id = consumer.memberid()
    for p in partitions:
        print(
            f"Consumer {cons_id} assigned to the topic: {p.topic}, partition {p.partition}."
        )
    consumer.assign(partitions)


def on_lost(consumer: Consumer, partitions: list[TopicPartition]) -> None:
    cons_id = consumer.memberid()
    for p in partitions:
        print(
            f"Consumer {cons_id} lost the topic: {p.topic}, partition {p.partition}."
        )


def on_revoke(consumer: Consumer, partitions: list[TopicPartition]) -> None:
    consumer.commit()
    cons_id = consumer.memberid()
    print(f"Consumer {cons_id} will be rebalanced.")
    consumer.unassign(partitions)


def check_topic_existence(consumer: Consumer, topic: str) -> None:
    while True:
        try:
            # We should use poll to get keycloak token for authorization on broker
            # https://github.com/confluentinc/confluent-kafka-python/issues/1713
            consumer.poll(1)
            topics: dict[str, TopicMetadata] = consumer.list_topics(
                timeout=5
            ).topics
            if topic in topics.keys():
                print(f"Topic:{topic} discovered successfully.")
                break
            else:
                print(
                    f"Topic:{topic} not found. Waiting 60 seconds before retrying."
                )
                sleep(60)
        except KafkaException as ex:
            print(f"Kafka Exception on Start: {ex}")
            sleep(60)
        except Exception as ex:
            print(f"Python Exception on Start: {ex}")
            sleep(60)


def parse_key_message(key: bytes) -> tuple[str, str]:
    """Return 'TMO:delete' or empty string"""
    result = "", ""
    if key is None:
        return result
    decoded_msg_key = key.decode("utf-8")
    if decoded_msg_key.find(":") == -1:
        print("Message key is not correct for this MS.")
        return result
    entity_type, operation = decoded_msg_key.split(":")
    return entity_type, operation


def is_relevant_message_type(entity_type: str, operation: str) -> bool:
    relevant: bool = False
    allowed_entities: set[str] = {
        "TMO",
        "TPRM",
    }
    allowed_operations: set[str] = {
        "deleted",
        "updated",
    }
    if entity_type in allowed_entities and operation in allowed_operations:
        relevant = True
    return relevant


if __name__ == "__main__":
    print("Kafka consumer - start")
    asyncio.run(run_kafka_cons_inv())
