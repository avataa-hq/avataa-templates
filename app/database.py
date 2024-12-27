import os
from dotenv import load_dotenv
from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


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
        },
    )
    session_factory = async_sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
