from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import SQLAlchemyUoW, UoW
from database import get_session_factory


# Common
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_unit_of_work(session: AsyncSession = Depends(get_async_session)) -> UoW:
    return SQLAlchemyUoW(session)
