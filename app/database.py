from functools import lru_cache

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)

from config import setup_config

convention = {
    "ix": "ix_%(column_0_label)s",  # INDEX
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # UNIQUE
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # CHECK
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",  # FOREIGN KEY
    "pk": "pk_%(table_name)s",  # PRIMARY KEY
}


class Base(DeclarativeBase, MappedAsDataclass):
    metadata = MetaData(naming_convention=convention)


@lru_cache()
def get_engine() -> AsyncEngine:
    echo_value = True
    if setup_config().app.logging > 20:
        echo_value = False

    engine = create_async_engine(
        url=setup_config().DATABASE_URL.unicode_string(),
        echo=echo_value,
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


@lru_cache()
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )
