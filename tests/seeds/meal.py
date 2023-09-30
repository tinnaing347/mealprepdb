from aiodal import dal
import sqlalchemy as sa
import datetime


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    x = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
    tab = trans.get_table("meal")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {
                    "id": 1,
                    "type": "dinner",
                    "description": "mong bean and rice with ham",
                    "consumed_on": x("2017-07-01"),
                },
                {
                    "id": 2,
                    "type": "dinner",
                    "description": "mong bean and rice with ham",
                    "consumed_on": x("2017-07-02"),
                },
                {
                    "id": 3,
                    "type": "dinner",
                    "description": "rice with ham and chickpeas",
                    "consumed_on": x("2017-07-03"),
                },
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('meal_id_seq', 3)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("meal")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('meal_id_seq', 1)"))
