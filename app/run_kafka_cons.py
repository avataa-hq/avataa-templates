import asyncio
import functools

from confluent_kafka import Consumer

from database import session_factory
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
    async_session = SQLAlchemyUoW(
        session_factory=session_factory
    )
    template_object_service = (
        TemplateObjectService(uow=async_session)
    )
    template_parameter_service = (
        TemplateParameterService(
            uow=async_session
        )
    )
    if kafka_config.turn_on:
        print("Kafka turn on")
        loop = asyncio.get_running_loop()
        consumer_config = kafka_config.model_dump(
            by_alias=True,
            exclude={
                "turn_on",
                "inventory_changes_topic",
                "with_keycloak",
            },
        )
        if not kafka_config.with_keycloak:
            consumer_config.pop("sasl.mechanisms")
        kafka_inventory_changes_consumer = (
            Consumer(consumer_config)
        )
        try:
            kafka_inventory_changes_consumer.subscribe(
                [
                    kafka_config.inventory_changes_topic
                ]
            )
            while True:
                poll = functools.partial(
                    kafka_inventory_changes_consumer.poll,
                    3.0,
                )
                msg = await loop.run_in_executor(
                    None, poll
                )
                if msg is None:
                    continue
                handler_inst = (
                    InventoryChangesHandler(
                        kafka_msg=msg
                    )
                )
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


if __name__ == "__main__":
    print("Kafka consumer - start")
    asyncio.run(run_kafka_cons_inv())
