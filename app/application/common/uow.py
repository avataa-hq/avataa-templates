from abc import ABC, abstractmethod

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


class SQLAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            if not self._committed:
                await self.rollback()

        await self.session.close()

    async def commit(self):
        await self.session.commit()
        self._committed = True

    async def rollback(self):
        await self.session.rollback()
