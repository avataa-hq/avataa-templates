from functools import wraps
from logging import getLogger
from typing import Awaitable, Callable, ParamSpec, TypeVar

from sqlalchemy.exc import (
    IntegrityError,
    ProgrammingError,
    TimeoutError,
)

T = TypeVar("T")
P = ParamSpec("P")


def handle_db_exceptions(
    func: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger = getLogger(func.__module__)
        try:
            return await func(*args, **kwargs)
        except IntegrityError as ex:
            logger.error(f"Integrity error in function {func.__name__}: {ex}.")
            raise ValueError(f"{ex.orig}, {ex.params}, {ex.statement}")
        except ProgrammingError as ex:
            logger.error(
                f"Programming error in function {func.__name__}: {ex}."
            )
            raise ValueError(f"{ex.orig}, {ex.params}, {ex.statement}")
        except TimeoutError:
            msg = "Can't connect to DB. Timeout Error"
            logger.error(f"{msg}.")
            raise ValueError("Can't connect to DB. Timeout Error")
        except Exception as ex:
            logger.error(f"Unexpected error in function {func.__name__}: {ex}.")
            raise

    return wrapper
