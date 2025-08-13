from abc import ABC, abstractmethod
from typing import Any, Callable, Self

from sqlalchemy.ext.asyncio import AsyncSession


class UoW(ABC):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class SQLAlchemyUoW(UoW):
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
    ):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        return self

    async def __aexit__(self: Self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        if self.session:
            await self.session.close()

    def __getattr__(self, name: str) -> Any:
        if self.session is None:
            raise RuntimeError(
                "Session not initialized. Use 'async with' context manager."
            )
        return getattr(self.session, name)

    async def commit(self: Self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self: Self) -> None:
        if self.session:
            await self.session.rollback()

    async def flush(self: Self) -> None:
        if self.session:
            await self.session.flush()
