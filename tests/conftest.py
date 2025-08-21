from typing import AsyncIterator
from unittest.mock import patch

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from main import v1_app as real_app
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.postgres import (
    PostgresContainer,
)

from config import setup_config
from di import get_async_session
from models import Base


@pytest_asyncio.fixture(scope="session")
def db_url():
    if setup_config().tests.run_container_postgres_local:
        with PostgresContainer(
            username=setup_config().tests.user,
            password=setup_config().tests.db_pass,
            dbname="test_db",
            driver="asyncpg",
        ) as postgres:
            yield postgres.get_connection_url()
    else:
        db_url = setup_config().test_database_url.unicode_string()
        yield db_url


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine(db_url) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        url=db_url,
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def test_session(
    test_engine: AsyncEngine,
):
    """Create test database session"""
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# only for pytest-asyncio 0.21/0.23
# @pytest.fixture(scope="session")
# def event_loop():
#     """Function that creates new event loop if it is not exist
#     .. note::/
#         It is needed for async tests
#     """
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def mock_grpc_response() -> AsyncIterator:
    with (
        patch(
            "services.template_registry_services.get_all_tmo_data_from_inventory_channel_in"
        ) as get_all_tmo_data_from_inventory,
        patch(
            "services.template_registry_services.get_all_tprms_for_special_tmo_id_channel_in"
        ) as get_all_tprms_for_special_tmo_id,
    ):
        yield (
            get_all_tmo_data_from_inventory,
            get_all_tprms_for_special_tmo_id,
        )


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def app(test_session, mock_grpc_response, test_engine) -> FastAPI:
    real_app.dependency_overrides[get_async_session] = lambda: test_session
    return real_app


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def async_client(
    app: FastAPI,
) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
