from abc import ABC, abstractmethod
from typing import Self

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
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self: Self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self: Self) -> None:
        if self.session:
            await self.session.rollback()

    async def flush(self: Self) -> None:
        if self.session:
            await self.session.flush()
