from aiodal import dal
import sqlalchemy as sa
import datetime


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    x = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
    tab = trans.get_table("meal_ingredient")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {"meal_id": 1, "ingredient_id": 5, "quantity": 0.33, "unit": "percent"},
                {"meal_id": 2, "ingredient_id": 5, "quantity": 0.33, "unit": "percent"},
                {"meal_id": 3, "ingredient_id": 5, "quantity": 0.33, "unit": "percent"},
                {"meal_id": 3, "ingredient_id": 6, "quantity": 1, "unit": "percent"},
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('meal_ingredient_id_seq', 4)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("meal_ingredient")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('meal_ingredient_id_seq', 1)"))
