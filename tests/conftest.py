import pathlib
from mealprepdb import config as appconfig
import pytest
from aiodal import dal

import os

this_dir = pathlib.Path(__file__).parent
root_dir = this_dir.parent

from mealprepdb import config
from mealprepdb.api import main, deps

import orjson
from mealprepdb.api.base import orjson_serializer

from .seeds import (
    fixture_load,
    ingredient,
    ingredient_in_inventory,
    dish,
    dish_ingredient,
)

import logging

logger = logging.getLogger(__name__)

# configure this seperately so we can connect and create a database first.
if appconfig.ENVIRONMENT != "testing":
    raise ValueError(
        "must set environment variable to `testing` in order to correctly configure test suite"
    )


# need this to keep event loop for the duration of the tests
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def engine_uri():
    return config.POSTGRES_URI


@pytest.fixture(scope="session")
def engine_extra_kwargs():
    """Any extra kwargs for the engine you want for your tests. Defaults to empty.

    Returns:
        Dict[str, Any]: Extra engine kwargs.
    """
    return {
        "json_serializer": orjson_serializer,
        "echo": False,
        "json_deserializer": orjson.loads,
    }


@pytest.fixture(scope="module")
async def module_transaction(db):
    """auto rollback. Module level isolation"""
    async with db.engine.connect() as conn:
        transaction = dal.TransactionManager(conn, db)
        try:
            yield transaction
        finally:
            await transaction.rollback()


@pytest.fixture(scope="module")
def module_get_transaction(module_transaction):
    """override dep injector"""

    async def _get_test_transaction():
        return module_transaction

    return _get_test_transaction


@pytest.fixture(scope="module")
def module_test_app(module_get_transaction):
    main.app.dependency_overrides[deps.get_transaction] = module_get_transaction
    yield main.app
    main.app.dependency_overrides = {}


@pytest.fixture(scope="module")
async def module_ingredient_data(module_transaction):
    await fixture_load(module_transaction, ingredient, ingredient_in_inventory)


@pytest.fixture(scope="module")
async def module_dish_data(module_transaction):
    await fixture_load(
        module_transaction, ingredient, ingredient_in_inventory, dish, dish_ingredient
    )
