from aiodal import dal
import sqlalchemy as sa
import datetime


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    x = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
    tab = trans.get_table("dish")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {
                    "id": 1,
                    "name": "mong bean and rice",
                    "parent_dish_id": None,
                    "created_on": x("2017-07-01"),
                },
                {
                    "id": 2,
                    "name": "plain rice",
                    "parent_dish_id": None,
                    "created_on": x("2017-07-03"),
                },
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('dish_id_seq', 2)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("dish")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('dish_id_seq', 1)"))
