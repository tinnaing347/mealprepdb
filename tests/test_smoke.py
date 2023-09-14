import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.anyio


@pytest.mark.anyio
async def test_transaction_smoke(module_transaction):
    transaction = module_transaction
