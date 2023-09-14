from fastapi import HTTPException
from aiodal import dal
from typing import AsyncIterator
import logging
from aiodal.oqm.views import AiodalHTTPException

logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s, %(levelname)s - %(message)s"
)

db = dal.DataAccessLayer()

from fastapi.exceptions import RequestValidationError


# this are the exceptions we are expected to handle..
CUSTOM_EXCEPTIONS = (
    HTTPException,
    RequestValidationError,
    AiodalHTTPException,
)


async def get_transaction() -> AsyncIterator[dal.TransactionManager]:
    """Dependency Injector for fastapi routes.

    Returns:
        AsyncIterator[AsyncConnection]: _description_

    Yields:
        Iterator[AsyncIterator[AsyncConnection]]: _description_
    """
    async with db.engine.connect() as conn:
        transaction = dal.TransactionManager(conn, db)
        try:
            yield transaction
            await transaction.commit()
        except CUSTOM_EXCEPTIONS:
            await transaction.rollback()
            raise
        except Exception as err:
            logging.exception(err)
            await transaction.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
