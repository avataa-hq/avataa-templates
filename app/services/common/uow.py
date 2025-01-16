from abc import ABC, abstractmethod
from typing import Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession


class UoW(ABC):
    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def flush(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class SQLAlchemyUoW(UoW):
    def __init__(
        self,
        session_factory: Callable[
            [], AsyncSession
        ],
    ):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(
        self, exc_type, exc_val, exc_tb
    ):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    def __getattr__(self, name: str) -> Any:
        if self.session is None:
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )
        return getattr(self.session, name)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def flush(self):
        await self.session.flush()
