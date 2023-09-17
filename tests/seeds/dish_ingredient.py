from aiodal import dal
import sqlalchemy as sa
import datetime


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    x = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
    tab = trans.get_table("dish_ingredient")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {
                    "id": 1,
                    "dish_id": 1,
                    "ingredient_id": 1,
                    "quantity": 1.5,
                    "unit": "pound",
                },
                {
                    "id": 2,
                    "dish_id": 1,
                    "ingredient_id": 3,
                    "quantity": 2,
                    "unit": "cups",
                },
                {
                    "id": 3,
                    "dish_id": 1,
                    "ingredient_id": 4,
                    "quantity": 1,
                    "unit": "cups",
                },
                {
                    "id": 4,
                    "dish_id": 2,
                    "ingredient_id": 3,
                    "quantity": 2,
                    "unit": "cups",
                },
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('dish_ingredient_id_seq', 4)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("dish_ingredient")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('dish_ingredient_id_seq', 1)"))
