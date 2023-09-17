from aiodal import dal
import sqlalchemy as sa


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("ingredient")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {"id": 1, "name": "onion", "type": "base_vegetable"},
                {"id": 2, "name": "rice", "type": "starch"},
                {"id": 3, "name": "cumin", "type": "spice"},
                {"id": 4, "name": "mong beans", "type": "legumes"},
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('ingredient_id_seq', 4)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("ingredient")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('ingredient_id_seq', 1)"))
