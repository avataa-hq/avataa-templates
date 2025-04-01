import asyncio
import functools

from time import sleep

from confluent_kafka import Consumer, TopicPartition, KafkaException
from confluent_kafka.admin import TopicMetadata

from di import build_session_factory
from services.common.uow import SQLAlchemyUoW
from services.inventory_services.db_services import (
    TemplateObjectService,
    TemplateParameterService,
)
from services.inventory_services.kafka.consumer.config import (
    KafkaConfig,
)
from services.inventory_services.kafka.consumer.utils import (
    InventoryChangesHandler,
)


async def run_kafka_cons_inv() -> None:
    kafka_config = KafkaConfig()
    async_session = SQLAlchemyUoW(session_factory=build_session_factory)
    template_object_service = TemplateObjectService(uow=async_session)
    template_parameter_service = TemplateParameterService(uow=async_session)
    if kafka_config.turn_on:
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
        consumer_config = kafka_config.model_dump(
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
                poll = functools.partial(
                    kafka_inventory_changes_consumer.poll,
                    3.0,
                )
                msg = await loop.run_in_executor(None, poll)
                if msg is None:
                    continue
                handler_inst = InventoryChangesHandler(kafka_msg=msg)
                await handler_inst.process_the_message(
                    template_object_service=template_object_service,
                    template_parameter_service=template_parameter_service,
                )
                kafka_inventory_changes_consumer.commit(
                    asynchronous=True, message=msg
                )
        except (
            KeyboardInterrupt,
            asyncio.CancelledError,
        ):
            kafka_inventory_changes_consumer.close()
            print("Kafka consumer - end")
    else:
        print("kafka turn off")


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


if __name__ == "__main__":
    print("Kafka consumer - start")
    asyncio.run(run_kafka_cons_inv())
