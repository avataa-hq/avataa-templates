from typing import AsyncGenerator

from confluent_kafka import Consumer
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import SQLAlchemyUoW
from application.exporter.interactors import ObjectTemplateExportInteractor
from application.importer.interactors import (
    ObjectTemplateImportInteractor,
    ObjectTemplateImportValidationInteractor,
)
from application.inventory_changes.interactors import InventoryChangesInteractor
from application.template.read.interactors import TemplateReaderInteractor
from application.template.update.interactors import TemplateUpdaterInteractor
from application.template_object.create.interactors import (
    TemplateObjectCreatorInteractor,
)
from application.template_object.delete.interactors import (
    TemplateObjectDeleterInteractor,
)
from application.template_object.read.interactors import (
    TemplateObjectByIdReaderInteractor,
    TemplateObjectByObjectTypeReaderInteractor,
    TemplateObjectReaderInteractor,
)
from application.template_object.update.interactors import (
    TemplateObjectUpdaterInteractor,
)
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
from application.template_parameter.delete.interactors import (
    TemplateParameterDeleterInteractor,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from application.template_parameter.update.interactors import (
    BulkTemplateParameterUpdaterInteractor,
    TemplateParameterUpdaterInteractor,
)
from application.tmo_validation.interactors import TMOValidationInteractor
from application.tprm_validation.interactors import (
    ParameterValidationInteractor,
)
from database import get_session_factory
from domain.exporter.enrich_service import OTEnrichService
from domain.exporter.export_service import ObjectTemplateExportService
from domain.exporter.query import DataFormatter
from domain.importer.enrich_service import OTEnrichErrorService
from domain.importer.validate_service import (
    TemplateImportValidationService,
)
from domain.template.command import TemplateUpdater
from domain.template.query import TemplateReader
from domain.template_object.command import (
    TemplateObjectCreator,
    TemplateObjectDeleter,
    TemplateObjectUpdater,
)
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import (
    TemplateParameterCreator,
    TemplateParameterDeleter,
    TemplateParameterUpdater,
)
from domain.template_parameter.query import TemplateParameterReader
from domain.template_parameter.service import TemplateParameterValidityService
from domain.tmo_validation.query import TMOReader
from domain.tprm_validation.query import TPRMReader
from infrastructure.db.template.read.gateway import SQLTemplateReaderRepository
from infrastructure.db.template.update.gateway import (
    SQLTemplateUpdaterRepository,
)
from infrastructure.db.template_object.create.gateway import (
    SQLTemplateObjectCreatorRepository,
)
from infrastructure.db.template_object.delete.gateway import (
    SQLTemplateObjectDeleterRepository,
)
from infrastructure.db.template_object.read.gateway import (
    SQLTemplateObjectReaderRepository,
)
from infrastructure.db.template_object.update.gateway import (
    SQLTemplateObjectUpdaterRepository,
)
from infrastructure.db.template_parameter.create.gateway import (
    SQLTemplateParameterCreatorRepository,
)
from infrastructure.db.template_parameter.delete.gateway import (
    SQLTemplateParameterDeleterRepository,
)
from infrastructure.db.template_parameter.read.gateway import (
    SQLTemplateParameterReaderRepository,
)
from infrastructure.db.template_parameter.update.gateway import (
    SQLTemplateParameterUpdaterRepository,
)
from infrastructure.formatter.export_gateway import ExcelDataFormatter
from infrastructure.grpc.tmo.read.gateway import GrpcTMOReaderRepository
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
    def get_tprm_inventory_repo(self) -> TPRMReader:
        return GrpcTPRMReaderRepository()

    @provide(scope=Scope.REQUEST)
    def get_tmo_inventory_repo(self) -> TMOReader:
        return GrpcTMOReaderRepository()

    ## Formatter Repo
    @provide(scope=Scope.REQUEST)
    def get_formatter_repo(self) -> DataFormatter:
        return ExcelDataFormatter()

    ## Template Repo
    @provide(scope=Scope.REQUEST)
    def get_template_reader_repo(self, session: AsyncSession) -> TemplateReader:
        return SQLTemplateReaderRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_updater_repo(
        self, session: AsyncSession
    ) -> TemplateUpdater:
        return SQLTemplateUpdaterRepository(session)

    ## Template object Repo
    @provide(scope=Scope.REQUEST)
    def get_template_object_creator_repo(
        self, session: AsyncSession
    ) -> TemplateObjectCreator:
        return SQLTemplateObjectCreatorRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_object_reader_repo(
        self, session: AsyncSession
    ) -> TemplateObjectReader:
        return SQLTemplateObjectReaderRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_object_updater_repo(
        self, session: AsyncSession
    ) -> TemplateObjectUpdater:
        return SQLTemplateObjectUpdaterRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_object_deleter_repo(
        self, session: AsyncSession
    ) -> TemplateObjectDeleter:
        return SQLTemplateObjectDeleterRepository(session)

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
    def get_template_parameter_updater_repo(
        self, session: AsyncSession
    ) -> TemplateParameterUpdater:
        return SQLTemplateParameterUpdaterRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_deleter_repo(
        self, session: AsyncSession
    ) -> TemplateParameterDeleter:
        return SQLTemplateParameterDeleterRepository(session)


class InteractorProvider(Provider):
    ## Data Enricher
    @provide(scope=Scope.REQUEST)
    def get_enricher(
        self,
        tmo_repo: TMOReader,
        tprm_reader: TPRMReader,
    ) -> OTEnrichService:
        return OTEnrichService(
            tmo_repo,
            tprm_reader,
        )

    @provide(scope=Scope.REQUEST)
    def get_enricher_validation(
        self,
    ) -> OTEnrichErrorService:
        return OTEnrichErrorService()

    ## Validate
    @provide(scope=Scope.REQUEST)
    def get_validate_service(
        self,
        t_reader: TemplateReader,
        tmo_repo: TMOReader,
        tprm_repo: TPRMReader,
    ) -> TemplateImportValidationService:
        return TemplateImportValidationService(
            t_reader=t_reader,
            tmo_reader=tmo_repo,
            tprm_reader=tprm_repo,
        )

    ## Export Interactor
    @provide(scope=Scope.REQUEST)
    def get_ot_exporter(
        self,
        ot_exporter: ObjectTemplateExportService,
        data_formatter: DataFormatter,
        enricher: OTEnrichService,
    ) -> ObjectTemplateExportInteractor:
        return ObjectTemplateExportInteractor(
            ot_exporter, data_formatter, enricher
        )

    ## Import Interactor
    @provide(scope=Scope.REQUEST)
    def get_ot_importer(
        self,
    ) -> ObjectTemplateImportInteractor:
        return ObjectTemplateImportInteractor()

    @provide(scope=Scope.REQUEST)
    def get_ot_validator(
        self,
        validation_service: TemplateImportValidationService,
        data_formatter: DataFormatter,
        enricher: OTEnrichErrorService,
    ) -> ObjectTemplateImportValidationInteractor:
        return ObjectTemplateImportValidationInteractor(
            validation_service=validation_service,
            data_formatter=data_formatter,
            enricher=enricher,
        )

    ## ParameterValidator Interactor
    @provide(scope=Scope.REQUEST)
    def get_parameter_validator(
        self, tprm_repo: TPRMReader
    ) -> ParameterValidationInteractor:
        return ParameterValidationInteractor(tprm_repo=tprm_repo)

    @provide(scope=Scope.REQUEST)
    def get_tmo_validator(
        self, grpc_repo: TMOReader
    ) -> TMOValidationInteractor:
        return TMOValidationInteractor(grpc_repo)

    ## Template Interactor
    @provide(scope=Scope.REQUEST)
    def get_template_reader(
        self, repo: TemplateReader
    ) -> TemplateReaderInteractor:
        return TemplateReaderInteractor(repo)

    @provide(scope=Scope.REQUEST)
    def get_template_updater(
        self,
        tmo_validator: TMOValidationInteractor,
        t_reader: TemplateReader,
        t_updater: TemplateUpdater,
        uow: SQLAlchemyUoW,
    ) -> TemplateUpdaterInteractor:
        return TemplateUpdaterInteractor(
            tmo_validator=tmo_validator,
            t_reader=t_reader,
            t_updater=t_updater,
            uow=uow,
        )

    ## Template Object Interactor
    @provide(scope=Scope.REQUEST)
    def get_template_object_creator(
        self,
        to_creator: TemplateObjectCreator,
        uow: SQLAlchemyUoW,
    ) -> TemplateObjectCreatorInteractor:
        return TemplateObjectCreatorInteractor(
            to_creator=to_creator,
            uow=uow,
        )

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
    ) -> TemplateObjectByIdReaderInteractor:
        return TemplateObjectByIdReaderInteractor(
            to_repo=to_repo, tp_repo=tp_repo
        )

    @provide(scope=Scope.REQUEST)
    def get_template_object_by_object_type_reader(
        self,
        to_repo: TemplateObjectReader,
    ) -> TemplateObjectByObjectTypeReaderInteractor:
        return TemplateObjectByObjectTypeReaderInteractor(to_repo=to_repo)

    @provide(scope=Scope.REQUEST)
    def get_template_object_updater(
        self,
        tmo_validator: TMOValidationInteractor,
        to_reader: TemplateObjectReader,
        to_updater: TemplateObjectUpdater,
        uow: SQLAlchemyUoW,
    ) -> TemplateObjectUpdaterInteractor:
        return TemplateObjectUpdaterInteractor(
            tmo_validator=tmo_validator,
            to_reader=to_reader,
            to_updater=to_updater,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_template_object_deleter(
        self,
        to_reader: TemplateObjectReader,
        to_deleter: TemplateObjectDeleter,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> TemplateObjectDeleterInteractor:
        return TemplateObjectDeleterInteractor(
            to_reader=to_reader,
            to_deleter=to_deleter,
            tp_validity_service=tp_validity_service,
            uow=uow,
        )

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
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterUpdaterInteractor:
        return TemplateParameterUpdaterInteractor(
            to_reader=to_reader,
            tp_reader=tp_reader,
            tp_updater=tp_updater,
            tprm_validator=tprm_validator,
            tp_validity_service=tp_validity_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_bulk_updater(
        self,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        tprm_validator: ParameterValidationInteractor,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> BulkTemplateParameterUpdaterInteractor:
        return BulkTemplateParameterUpdaterInteractor(
            to_reader=to_reader,
            tp_reader=tp_reader,
            tp_updater=tp_updater,
            tprm_validator=tprm_validator,
            tp_validity_service=tp_validity_service,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_template_parameter_deleter(
        self,
        tp_reader: TemplateParameterReader,
        tp_deleter: TemplateParameterDeleter,
        tp_validity_service: TemplateParameterValidityService,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterDeleterInteractor:
        return TemplateParameterDeleterInteractor(
            tp_deleter=tp_deleter,
            tp_reader=tp_reader,
            tp_validity_service=tp_validity_service,
            uow=uow,
        )

    # Domain Service
    @provide(scope=Scope.REQUEST)
    def get_template_validity_service(
        self,
        t_reader: TemplateReader,
        t_updater: TemplateUpdater,
        to_reader: TemplateObjectReader,
        to_updater: TemplateObjectUpdater,
        tp_reader: TemplateParameterReader,
        tp_updater: TemplateParameterUpdater,
        uow: SQLAlchemyUoW,
    ) -> TemplateParameterValidityService:
        return TemplateParameterValidityService(
            t_reader=t_reader,
            t_updater=t_updater,
            to_reader=to_reader,
            to_updater=to_updater,
            tp_reader=tp_reader,
            tp_updater=tp_updater,
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_ot_export_service(
        self,
        t_reader: TemplateReader,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
    ) -> ObjectTemplateExportService:
        return ObjectTemplateExportService(
            t_reader=t_reader,
            to_reader=to_reader,
            tp_reader=tp_reader,
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

    @provide(scope=Scope.REQUEST)
    def get_inventory_changes_interactor(
        self,
        tp_validity_service: TemplateParameterValidityService,
        to_service: TemplateObjectService,
        tp_service: TemplateParameterService,
        uow: SQLAlchemyUoW,
    ) -> InventoryChangesInteractor:
        return InventoryChangesInteractor(
            tp_validity_service=tp_validity_service,
            to_service=to_service,
            tp_service=tp_service,
            uow=uow,
        )


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
