import asyncio
from datetime import datetime
import functools
from time import sleep

from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition
from confluent_kafka.admin import TopicMetadata
from dishka import make_async_container

from application.common.uow import SQLAlchemyUoW
from database import get_session_factory
from infrastructure.di.providers import (
    DatabaseProvider,
    KafkaProvider,
    KafkaServiceProvider,
)
from services.inventory_services.db_services import (
    TemplateObjectService,
    TemplateParameterService,
)
from services.inventory_services.kafka.consumer.config import (
    KafkaConfig,
)
from services.inventory_services.kafka.consumer.msg_protocol import (
    KafkaMSGProtocol,
)
from services.inventory_services.kafka.consumer.utils import (
    InventoryChangesConverter,
    InventoryChangesHandler,
)


async def run_kafka_cons_old() -> None:
    kafka_config = KafkaConfig()

    if not kafka_config.turn_on:
        print("kafka turn off")
        return
    print("Kafka turn on")
    loop = asyncio.get_running_loop()
    dump_set = {
        "bootstrap_servers",
        "group_id",
        "auto_offset_reset",
        "enable_auto_commit",
    }
    if kafka_config.secured:
        dump_set.update(
            {
                "sasl_mechanism",
                "oauth_cb",
            }
        )
    consumer_config = kafka_config.get_config(
        by_alias=True,
        exclude_none=True,
        include=dump_set,
    )
    kafka_inventory_changes_consumer = Consumer(consumer_config)
    try:
        check_topic_existence(
            consumer=kafka_inventory_changes_consumer,
            topic=kafka_config.inventory_changes_topic,
        )
        kafka_inventory_changes_consumer.subscribe(
            [kafka_config.inventory_changes_topic],
            on_assign=on_assign,
            on_revoke=on_revoke,
            on_lost=on_lost,
        )
        while True:
            poll = functools.partial(kafka_inventory_changes_consumer.poll, 3.0)
            msg = await loop.run_in_executor(None, poll)
            if msg is None:
                continue
            if not msg.key:
                kafka_inventory_changes_consumer.commit(
                    asynchronous=True, message=msg
                )
                continue
            key = parse_key_message(msg.key())
            if not is_relevant_message_type(key):
                kafka_inventory_changes_consumer.commit(
                    asynchronous=True, message=msg
                )
                print(f"{datetime.now()} Skip message {msg.offset()}")
                continue
            success = await process_single_message(message=msg, key=key)
            if success:
                kafka_inventory_changes_consumer.commit(
                    asynchronous=True, message=msg
                )
            else:
                print(
                    f"Skipping message {msg.offset()} due to processing error"
                )
    except (KeyboardInterrupt, asyncio.CancelledError):
        kafka_inventory_changes_consumer.close()
        print("Kafka consumer - end")


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
            if test_msg.error().code() == KafkaError._PARTITION_EOF:
                print("Kafka connection OK (reached end of partition)")
            else:
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
        DatabaseProvider(), KafkaProvider(), KafkaServiceProvider()
    )
    message_batch: list[tuple[KafkaMSGProtocol, str]] = []
    batch_size = 100
    loop = asyncio.get_running_loop()
    async with container() as di:
        consumer = await di.get(Consumer)
        if not await initialize_kafka_consumer(consumer):
            print("Failed to initialize Kafka consumer. Exiting...")
            return
        try:
            while True:
                poll = functools.partial(consumer.poll, 3.0)
                msg = await loop.run_in_executor(None, poll)

                if msg is None:
                    if message_batch:
                        await process_batch_messages(message_batch, di)
                        message_batch.clear()
                    continue
                if not msg.key():
                    consumer.commit(asynchronous=True)
                    continue
                key = parse_key_message(msg.key())
                if not is_relevant_message_type(key):
                    consumer.commit(asynchronous=True)
                    continue
                message_batch.append((msg, key))
                if len(message_batch) >= batch_size:
                    await process_batch_messages(message_batch, di)
                    message_batch.clear()
                consumer.commit(asynchronous=False)
        except (KeyboardInterrupt, asyncio.CancelledError):
            if message_batch:
                await process_batch_messages(message_batch, di)
                print("Error processing final batch")
                # send dead letter
                message_batch.clear()
            print("Kafka consumer - end")


async def process_batch_messages(
    messages: list[tuple[KafkaMSGProtocol, str]], container
) -> bool:
    list_tprm = []
    list_tmo = []
    converter = InventoryChangesConverter()
    for msg, key in messages:
        entity_type, _ = key.split(":")
        if entity_type == "TMO":
            list_tmo.append(converter(msg, key))
        else:
            list_tprm.append(converter(msg, key))
    tmo_ids = list(
        {
            tmo.get("id")
            for message in list_tmo
            for tmo in message.get("objects", [])
        }
    )
    tprm_ids = list(
        {
            tprm.get("id")
            for message in list_tprm
            for tprm in message.get("objects", [])
        }
    )
    async with container() as nested_container:
        try:
            uow = await nested_container.get(SQLAlchemyUoW)
            template_object_service = await nested_container.get(
                TemplateObjectService
            )
            template_parameter_service = await nested_container.get(
                TemplateParameterService
            )
            if tmo_ids:
                await template_object_service.set_template_object_invalid(
                    tmo_ids
                )
            if tprm_ids:
                await template_parameter_service.set_template_parameter_invalid(
                    tprm_ids
                )
            await uow.commit()
        except Exception as ex:
            print(f"Error processing message: {ex}.")
            await uow.rollback()
            return False
    return True


async def process_single_message(message: KafkaMSGProtocol, key: str) -> bool:
    handler_inst = InventoryChangesHandler(kafka_msg=message, key=key)
    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            uow = SQLAlchemyUoW(session)
            template_object_service = TemplateObjectService(session=uow.session)
            template_parameter_service = TemplateParameterService(
                session=uow.session
            )

            await handler_inst.process_the_message(
                template_object_service=template_object_service,
                template_parameter_service=template_parameter_service,
            )
            await uow.commit()
            print(f"Successfully processed message: {message.offset()}")
        except Exception as ex:
            print(f"Error processing message  {message.offset()}: {ex}.")
            await uow.rollback()
            return False
    if session.is_active:
        await uow.rollback()
    return True


def on_assign(consumer: Consumer, partitions: list[TopicPartition]) -> None:
    cons_id = consumer.memberid()
    for p in partitions:
        print(
            f"Consumer {cons_id} assigned to the topic: {p.topic}, partition {p.partition}."
        )


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


def parse_key_message(key: bytes) -> str:
    """Return 'TMO:delete' or empty string"""
    result = ""
    if key is None:
        return result
    decoded_msg_key = key.decode("utf-8")
    if decoded_msg_key.find(":") == -1:
        print("Message key is not correct for this MS.")
        return result
    return decoded_msg_key


def is_relevant_message_type(key: str) -> bool:
    relevant: bool = False
    allowed_keys: set[str] = {
        "TMO:updated",
        "TMO:deleted",
        "TPRM:updated",
        "TPRM:deleted",
    }
    if key in allowed_keys:
        relevant = True
    return relevant


if __name__ == "__main__":
    print("Kafka consumer - start")
    asyncio.run(run_kafka_cons_inv())
