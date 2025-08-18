from functools import partial
from logging import getLogger
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from presentation.api.depends_stub import Stub
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from application.common.uow import SQLAlchemyUoW, UoW
from application.template.read.interactors import TemplateReaderInteractor
from application.template_object.read.interactors import (
    TemplateObjectReaderInteractor,
)
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from config import setup_config
from domain.inventory_tprm.query import TPRMReader
from domain.template_object.query import TemplateObjectReader
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
from infrastructure.grpc.config import init_grpc_services
from infrastructure.grpc.tprm.read.gateway import GrpcTPRMReaderRepository

logger = getLogger(__name__)


def create_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=setup_config().DATABASE_URL.unicode_string(),
        echo=True,
        max_overflow=15,
        pool_size=15,
        pool_pre_ping=True,
        connect_args={
            "server_settings": {
                "application_name": "Object Template MS",
                "search_path": setup_config().db.schema_name,
            },
        },
    )
    return engine


def build_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        logger.info("Create DB session.")
        try:
            yield session
        finally:
            logger.info("Close DB session.")


async def get_uow(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[UoW, None]:
    async with SQLAlchemyUoW(session_factory=session_factory) as uow:
        yield uow


def get_inventory_repository() -> TPRMReader:
    return GrpcTPRMReaderRepository()


def read_template_interactor(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TemplateReaderInteractor:
    repository = SQLTemplateReaderRepository(session)
    return TemplateReaderInteractor(repository)


def get_template_object_reader_repository(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TemplateObjectReader:
    return SQLTemplateObjectReaderRepository(session)


def get_template_parameter_reader_repository(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TemplateParameterReader:
    return SQLTemplateParameterReaderRepository(session)


def read_template_object_interactor(
    to_repository: TemplateObjectReader = Depends(
        get_template_object_reader_repository
    ),
    tp_repository: TemplateParameterReader = Depends(
        get_template_parameter_reader_repository
    ),
) -> TemplateObjectReaderInteractor:
    return TemplateObjectReaderInteractor(
        to_repo=to_repository, tp_repo=tp_repository
    )


def read_template_parameter_interactor(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TemplateParameterReaderInteractor:
    repository = SQLTemplateParameterReaderRepository(session)
    return TemplateParameterReaderInteractor(repository)


def create_template_parameter_interactor(
    uow: UoW = Depends(),
    to_repo: TemplateObjectReader = Depends(
        get_template_object_reader_repository
    ),
    inventory_repo: TPRMReader = Depends(get_inventory_repository),
) -> TemplateParameterCreatorInteractor:
    repository = SQLTemplateParameterCreatorRepository(uow.get_session())
    return TemplateParameterCreatorInteractor(
        to_repo=to_repo,
        tp_repo=repository,
        inventory_tprm_repo=inventory_repo,
        uow=uow,
    )


def init_dependencies(app: FastAPI) -> None:
    db_engine = create_engine()
    session_factory = build_session_factory(engine=db_engine)
    init_grpc_services()

    app.dependency_overrides[async_sessionmaker[AsyncSession]] = (
        lambda: session_factory
    )
    app.dependency_overrides[AsyncSession] = partial(
        get_session, session_factory
    )
    app.dependency_overrides[UoW] = partial(get_uow, session_factory)

    app.dependency_overrides[TPRMReader] = get_inventory_repository

    app.dependency_overrides[TemplateReaderInteractor] = (
        read_template_interactor
    )

    app.dependency_overrides[TemplateObjectReader] = (
        get_template_object_reader_repository
    )
    app.dependency_overrides[TemplateParameterReader] = (
        get_template_parameter_reader_repository
    )

    app.dependency_overrides[TemplateObjectReaderInteractor] = (
        read_template_object_interactor
    )

    app.dependency_overrides[TemplateParameterReaderInteractor] = (
        read_template_parameter_interactor
    )

    app.dependency_overrides[TemplateParameterCreatorInteractor] = (
        create_template_parameter_interactor
    )
