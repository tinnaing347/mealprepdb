from aiodal import dal
import sqlalchemy as sa
import datetime


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    x = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
    tab = trans.get_table("meal_dish")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {"meal_id": 1, "dish_id": 1, "quantity": 0.5, "unit": "percent"},
                {"meal_id": 2, "dish_id": 1, "quantity": 0.5, "unit": "percent"},
                {"meal_id": 2, "dish_id": 2, "quantity": 0.5, "unit": "percent"},
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('meal_dish_id_seq', 3)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("meal_dish")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('meal_dish_id_seq', 1)"))
