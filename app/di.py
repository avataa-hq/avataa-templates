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

from application.common.uow import UoW
from application.template.read.interactors import TemplateReaderInteractor
from config import setup_config
from infrastructure.db.template.read.gateway import SQLTemplateRepository

logger = getLogger(__name__)


def new_uow(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> AsyncSession:
    return session


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


async def new_session(
    session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


async def build_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        logger.info(msg="Create DB session.")
        yield session
        logger.info(msg="Close DB session.")


def read_template_interactor(
    session: AsyncSession = Depends(Stub(AsyncSession)),
) -> TemplateReaderInteractor:
    repository = SQLTemplateRepository(session)
    return TemplateReaderInteractor(repository)


def init_dependencies(app: FastAPI) -> None:
    db_engine = create_engine()
    session_factory = build_session_factory(engine=db_engine)

    app.dependency_overrides[AsyncSession] = partial(
        build_session, session_factory
    )
    app.dependency_overrides[UoW] = new_uow

    app.dependency_overrides[TemplateReaderInteractor] = (
        read_template_interactor
    )
