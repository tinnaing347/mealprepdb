from aiodal import dal
import sqlalchemy as sa
import datetime


async def load(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("ingredient_in_inventory")
    x = lambda s: datetime.datetime.strptime(s, "%Y-%m-%d")
    stmt = (
        sa.insert(tab)
        .values(
            [
                {
                    "id": 1,
                    "ingredient_id": 1,
                    "from_where": "onion ville",
                    "brand": "",
                    "price": 3.5,
                    "quantity": 1.5,
                    "unit": "pound",
                    "purchased_on": x("2017-07-01"),
                    "finished_on": x("2017-07-01"),
                },
                {
                    "id": 2,
                    "ingredient_id": 1,
                    "from_where": "leek ville",
                    "brand": "",
                    "price": 2,
                    "quantity": 1,
                    "unit": "pound",
                    "purchased_on": x("2017-07-05"),
                    "finished_on": x("2017-07-05"),
                },
                {
                    "id": 3,
                    "ingredient_id": 2,
                    "from_where": "onion ville",
                    "brand": "buen arroz",
                    "price": 23.99,
                    "quantity": 20,
                    "unit": "pound",
                    "purchased_on": x("2017-06-01"),
                    "finished_on": None,
                },
            ]
        )
        .returning(tab)
    )
    result = await trans.execute(stmt)
    await trans.execute(sa.text("select setval('ingredient_in_inventory_id_seq', 3)"))
    return result


async def unload(trans: dal.TransactionManager) -> sa.engine.CursorResult:
    tab = trans.get_table("ingredient_in_inventory")
    await trans.execute(sa.delete(tab))
    await trans.execute(sa.text("select setval('ingredient_in_inventory_id_seq', 1)"))
