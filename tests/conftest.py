from typing import AsyncIterator
from unittest.mock import patch

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport


from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool
from testcontainers.postgres import (
    PostgresContainer,
)

from main import app as real_app
from mocks.grpc_client import MockGrpcClient
from models import Base
from config import setup_config

if setup_config().tests.run_container_postgres_local:

    class DBContainer(PostgresContainer):
        @property
        def connection_url(
            self, host: str | None = None
        ) -> str:
            if not host:
                host = setup_config().tests.docker_db_host
            return str(
                super().get_connection_url(
                    host=host
                )
            )

    @pytest_asyncio.fixture(
        scope="session", loop_scope="session"
    )
    async def postgres_container() -> (
        AsyncIterator[DBContainer]
    ):
        postgres_container = DBContainer(
            username=setup_config().tests.user,
            password=setup_config().tests.db_pass,
            dbname="test_db",
            driver="asyncpg",
        )
        with postgres_container as container:
            yield container
            container.volumes.clear()

    @pytest_asyncio.fixture(
        scope="session", loop_scope="session"
    )
    async def test_engine(
        postgres_container: DBContainer,
    ) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            url=postgres_container.connection_url,
            poolclass=NullPool,
            echo=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.drop_all
            )
            await conn.run_sync(
                Base.metadata.create_all
            )

        yield engine

        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.drop_all
            )
        await engine.dispose()
else:

    @pytest_asyncio.fixture(
        scope="session", loop_scope="session"
    )
    async def test_engine() -> AsyncIterator[
        AsyncEngine
    ]:
        engine = create_async_engine(
            url=setup_config().test_database_url.unicode_string(),
            poolclass=NullPool,
            echo=False,
        )

        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.drop_all
            )
            await conn.run_sync(
                Base.metadata.create_all
            )

        yield engine

        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.drop_all
            )
        await engine.dispose()


@pytest_asyncio.fixture(
    scope="function", loop_scope="function"
)
async def test_session(
    test_engine: AsyncEngine,
) -> AsyncIterator[AsyncSession]:
    """Create test database session"""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        try:
            await session.rollback()
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


@pytest_asyncio.fixture(
    scope="session", loop_scope="session"
)
async def mock_grpc_client():
    return MockGrpcClient()


@pytest_asyncio.fixture(
    scope="session", loop_scope="session"
)
async def app(mock_grpc_client):
    with (
        patch(
            "grpc_clients.inventory.getters.getters_with_channel.get_all_tmo_data_from_inventory_channel_in",
            new=mock_grpc_client.get_all_tmo_data,
        ),
        patch(
            "grpc_clients.inventory.getters.getters_with_channel.get_all_tprms_for_special_tmo_id_channel_in",
            new=mock_grpc_client.get_all_tprms_for_tmo,
        ),
    ):
        # app = real_app
        # app.dependency_overrides[UoW] = test_session
        return real_app


@pytest_asyncio.fixture(
    scope="session", loop_scope="session"
)
async def async_client(
    app: FastAPI,
) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
