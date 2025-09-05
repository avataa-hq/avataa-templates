from typing import AsyncGenerator

from confluent_kafka import Consumer
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import SQLAlchemyUoW
from application.paramater_validation.interactors import (
    ParameterValidationInteractor,
)
from application.template.read.interactors import TemplateReaderInteractor
from application.template_object.read.interactors import (
    TemplateObjectByIdInteractor,
    TemplateObjectReaderInteractor,
)
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from application.template_parameter.update.interactors import (
    BulkTemplateParameterUpdaterInteractor,
    TemplateParameterUpdaterInteractor,
)
from database import get_session_factory
from domain.parameter_validation.query import TPRMReader
from domain.template.query import TemplateReader
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import (
    TemplateParameterCreator,
    TemplateParameterUpdater,
)
from domain.template_parameter.query import TemplateParameterReader
from infrastructure.db.template.read.gateway import SQLTemplateReaderRepository
from infrastructure.db.template_object.read.gateway import (
    SQLTemplateObjectReaderRepository,
)
from infrastructure.db.template_parameter.create.gateway import (
    SQLTemplateParameterCreatorRepository,
)
from infrastructure.db.template_parameter.read.gateway import (
    SQLTemplateParameterReaderRepository,
)
from infrastructure.db.template_parameter.update.gateway import (
    SQLTemplateParameterUpdaterRepository,
)
from infrastructure.grpc.tprm.read.gateway import GrpcTPRMReaderRepository
from services.inventory_services.db_services import (
    TemplateObjectService,
    TemplateParameterService,
)
from services.inventory_services.kafka.consumer.config import get_config


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @provide(scope=Scope.REQUEST)
    def get_uow(self, session: AsyncSession) -> SQLAlchemyUoW:
        return SQLAlchemyUoW(session)


class RepositoryProvider(Provider):
    ## Inventory Repo
    @provide(scope=Scope.REQUEST)
    def get_inventory_repo(self) -> TPRMReader:
        return GrpcTPRMReaderRepository()

    ## Template Repo
    @provide(scope=Scope.REQUEST)
    def get_template_reader_repo(self, session: AsyncSession) -> TemplateReader:
        return SQLTemplateReaderRepository(session)

    ## Template object Repo
    @provide(scope=Scope.REQUEST)
    def get_template_object_reader_repo(
        self, session: AsyncSession
    ) -> TemplateObjectReader:
        return SQLTemplateObjectReaderRepository(session)

    ## Template parameter Repo
    @provide(scope=Scope.REQUEST)
    def get_template_parameter_reader_repo(
        self, session: AsyncSession
    ) -> TemplateParameterReader:
        return SQLTemplateParameterReaderRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_creator_repo(
        self, session: AsyncSession
    ) -> TemplateParameterCreator:
        return SQLTemplateParameterCreatorRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_updater_repos(
        self, session: AsyncSession
    ) -> TemplateParameterUpdater:
        return SQLTemplateParameterUpdaterRepository(session)


class InteractorProvider(Provider):
    ## ParameterValidator Interactor
    @provide(scope=Scope.REQUEST)
    def get_parameter_validator(
        self, grpc_repo: TPRMReader
    ) -> ParameterValidationInteractor:
        return ParameterValidationInteractor(grpc_repo)

    ## Template Interactor
    @provide(scope=Scope.REQUEST)
    def get_template_reader(
        self, repo: TemplateReader
    ) -> TemplateReaderInteractor:
        return TemplateReaderInteractor(repo)

    ## Template Object Interactor
    @provide(scope=Scope.REQUEST)
    def get_template_object_reader(
        self,
        to_repo: TemplateObjectReader,
        tp_repo: TemplateParameterReader,
    ) -> TemplateObjectReaderInteractor:
        return TemplateObjectReaderInteractor(to_repo=to_repo, tp_repo=tp_repo)

    @provide(scope=Scope.REQUEST)
    def get_template_object_by_id_reader(
        self,
        to_repo: TemplateObjectReader,
        tp_repo: TemplateParameterReader,
    ) -> TemplateObjectByIdInteractor:
        return TemplateObjectByIdInteractor(to_repo=to_repo, tp_repo=tp_repo)

    ## Template Parameter Interactor
    @provide(scope=Scope.REQUEST)
    def get_template_parameter_creator(
        self,
        to_repo: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
        tp_creator: TemplateParameterCreator,
        tprm_validator: ParameterValidationInteractor,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterCreatorInteractor:
        return TemplateParameterCreatorInteractor(
            to_repo=to_repo,
            tp_creator=tp_creator,
            tp_reader=tp_reader,
            tprm_validator=tprm_validator,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_reader(
        self, tp_repo: TemplateParameterReader
    ) -> TemplateParameterReaderInteractor:
        return TemplateParameterReaderInteractor(tp_repo=tp_repo)

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_updater(
        self,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterUpdaterInteractor:
        return TemplateParameterUpdaterInteractor(
            tp_reader=tp_reader,
            to_reader=to_reader,
            tp_updater=tp_updater,
            tprm_validator=tprm_validator,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def bulk_update_template_parameter_interactor(
        self,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        uow: SQLAlchemyUoW,
    ) -> BulkTemplateParameterUpdaterInteractor:
        return BulkTemplateParameterUpdaterInteractor(
            to_reader=to_reader,
            tp_reader=tp_reader,
            tp_updater=tp_updater,
            tprm_validator=tprm_validator,
            uow=uow,
        )


class KafkaServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_template_object_service(
        self, session: AsyncSession
    ) -> TemplateObjectService:
        return TemplateObjectService(session=session)

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_service(
        self, session: AsyncSession
    ) -> TemplateParameterService:
        return TemplateParameterService(session=session)


class KafkaProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_kafka_consumer(self) -> AsyncGenerator[Consumer, None]:
        config = get_config()

        dump_set = {
            "bootstrap_servers",
            "group_id",
            "auto_offset_reset",
            "enable_auto_commit",
        }
        if config.secured:
            dump_set.update(
                {
                    "sasl_mechanism",
                    "method",
                    "scope",
                    "keycloak_client_id",
                    "keycloak_client_secret",
                    "keycloak_token_url",
                }
            )
        consumer_config = config.get_config(
            by_alias=True,
            exclude_none=True,
            include=dump_set,
        )
        consumer = Consumer(consumer_config)
        consumer.subscribe([config.inventory_changes_topic])

        print(
            f"Kafka Consumer created for group: {consumer_config['group.id']}"
        )

        try:
            yield consumer
        finally:
            print("Closing Kafka Consumer...")
            consumer.close()
