import sqlalchemy as sa


async def fixture_load(transaction, *modules):
    """Load all the given fixtures from their modules. Order matters!
    If you get integrity errors assure that the data gets inserted in the correct
    order based on FKs

    Args:
        transaction (_type_): _description_
    """
    for m in modules:
        await m.load(transaction)


async def fixture_unload(transaction, *modules):
    """For special cases when data is commited inside a test assures that
    the data is wiped before the next test begins.
    This must be called in a try:/finally block so that any commits that it is
    guarding are guaranteed to be deleted even if an assertion is failing.

    Args:
        transaction (_type_): _description_
    """
    for m in modules:
        await m.unload(transaction)
    await transaction.commit()
