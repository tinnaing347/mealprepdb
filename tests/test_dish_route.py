import httpx
import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.anyio


async def test_dish_list_view(module_test_app, module_dish_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_list_view")
        response = await client.get(path)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) > 0

        params = {"name__contains": "bean"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1


async def test_dish_detail_view(module_test_app, module_dish_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_detail_view", id=1)
        response = await client.get(path)
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "mong bean and rice"

        path = app.url_path_for("dish_detail_view", id=42)
        response = await client.get(path)
        assert response.status_code == 404


async def test_dish_ingredient_list_view(module_test_app, module_dish_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_ingredient_list_view", id=1)
        response = await client.get(path)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 3

        ingredient_names = ["rice", "mong beans", "onion"]

        for r in results:
            assert r["ingredient_name"] in ingredient_names

        params = {"ingredient_name": "rice"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1


async def test_dish_create_view(module_test_app, module_transaction, module_dish_data):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_create_view")
        # make more rice
        data = {"name": "plain rice", "created_on": "2017-07-04"}
        response = await client.post(path, json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["name"] == "plain rice"
        assert result["parent_dish_id"] == None
        assert result["created_on"] == "2017-07-04"

        # created_on missing
        data = {
            "name": "plain rice",
        }
        response = await client.post(path, json=data)
        assert response.status_code == 422

        # clean up
        t = transaction.get_table("dish")
        stmt = sa.delete(t).where(t.c.id == result["id"]).returning(t)
        res = await transaction.execute(stmt)
        obj_ = res.one()
        assert obj_.id == result["id"]


async def test_dish_update_view(module_test_app, module_transaction, module_dish_data):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_detail_view", id=2)
        res = await client.get(path)
        res = res.json()
        assert res["name"] == "plain rice"
        assert res["parent_dish_id"] == None

        path = app.url_path_for("dish_update_view", id=2)
        data = {
            "parent_dish_id": 1
        }  # not necessarily correct cooking wise but valid nonetheless in db
        response = await client.put(path, json=data)
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "plain rice"
        assert result["parent_dish_id"] == 1


async def test_dish_ingredient_create_view(
    module_test_app, module_transaction, module_dish_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_ingredient_create_view")

        # adding rice
        data = {
            "dish_id": 1,
            "ingredient_id": 2,
            "quantity": 1.5,
            "unit": "cup",
        }
        res = await client.post(path, json=data)
        assert res.status_code == 201
        result = res.json()
        assert result["dish_id"] == 1
        assert result["ingredient_id"] == 2
        assert result["quantity"] == 1.5
        assert result["unit"] == "cup"

        # clean up
        t = transaction.get_table("dish_ingredient")
        stmt = sa.delete(t).where(t.c.id == result["id"]).returning(t)
        res = await transaction.execute(stmt)
        obj_ = res.one()
        assert obj_.id == result["id"]


async def test_dish_create_view_409(
    module_test_app, module_transaction, module_dish_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_create_view")
        # make more rice
        data = {"name": "plain rice", "parent_dish_id": 42, "created_on": "2017-07-04"}
        response = await client.post(path, json=data)
        assert response.status_code == 409

        await transaction.rollback()


@pytest.mark.skip(reason="to do")
async def test_dish_update_view_409():
    # update on missing parent dish
    ...


@pytest.mark.skip(reason="to do")
async def test_dish_ingredient_create_view_409():
    ...
