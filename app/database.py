import os
from dotenv import load_dotenv
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedAsDataclass
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import setup_config

load_dotenv()

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


if DATABASE_URL:
    engine = create_async_engine(
        url=DATABASE_URL,
        echo=True,
        max_overflow=15,
        pool_size=15,
        pool_pre_ping=True,
        connect_args={
            "server_settings": {"application_name": "Object Template MS"},
            "options": f"-csearch_path={setup_config().db.DB_SCHEMA}",
        },
    )
    session_factory = async_sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

convention = {
    "ix": "ix_%(column_0_label)s",  # INDEX
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # UNIQUE
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # CHECK
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",  # FOREIGN KEY
    "pk": "pk_%(table_name)s",  # PRIMARY KEY
}


class Base(DeclarativeBase, MappedAsDataclass):
    metadata = MetaData(naming_convention=convention, schema=setup_config().db.DB_SCHEMA)


async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
