import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

if DATABASE_URL:
    async_engine = create_async_engine(
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
        bind=async_engine, autoflush=False, expire_on_commit=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
