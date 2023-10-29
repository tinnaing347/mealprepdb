import httpx
import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.anyio


async def test_meal_list_view(module_test_app, module_meal_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("meal_list_view")
        response = await client.get(path)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) > 0

        params = {"type": "dinner"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 3

        params = {"type": "lunch"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 0


async def test_meal_detail_view(module_test_app, module_meal_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("meal_detail_view", id=1)
        response = await client.get(path)
        assert response.status_code == 200

        result = response.json()
        assert result["description"] == "mong bean and rice with ham"

        path = app.url_path_for("meal_detail_view", id=42)
        response = await client.get(path)
        assert response.status_code == 404


async def test_meal_create_view(module_test_app, module_transaction, module_meal_data):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("meal_create_view")
        # democracy manifest
        data = {"description": "a succulent chinese meal", "consumed_on": "2017-07-04"}
        response = await client.post(path, json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["description"] == "a succulent chinese meal"
        assert result["consumed_on"] == "2017-07-04"

        # created_on missing
        data = {
            "description": "plain rice",
        }
        response = await client.post(path, json=data)
        assert response.status_code == 422

        # clean up
        t = transaction.get_table("meal")
        stmt = sa.delete(t).where(t.c.id == result["id"]).returning(t)
        res = await transaction.execute(stmt)
        obj_ = res.one()
        assert obj_.id == result["id"]


async def test_meal_update_view(module_test_app, module_transaction, module_meal_data):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        # as to not modify existing meal let's create one first
        path = app.url_path_for("meal_create_view")
        # democracy manifest
        data = {"description": "a succulent chinese meal", "consumed_on": "2017-07-04"}
        response = await client.post(path, json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["type"] == None

        created_obj_id = result["id"]

        path = app.url_path_for("meal_update_view", id=created_obj_id)
        data = {"type": "dinner"}
        res = await client.put(path, json=data)
        assert res.status_code == 200
        res = res.json()
        assert res["type"] == "dinner"
        assert res["description"] == "a succulent chinese meal"

        # clean up
        t = transaction.get_table("meal")
        stmt = sa.delete(t).where(t.c.id == created_obj_id).returning(t)
        res = await transaction.execute(stmt)
        obj_ = res.one()
        assert obj_.id == result["id"]


async def test_dish_meal_list_view(module_test_app, module_meal_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("dish_meal_list_view", id=1)
        response = await client.get(path)
        assert response.status_code == 200

        res = response.json()
        result = res["results"]
        assert len(result) == 2

        for r in result:
            assert r["dish_name"] == "mong bean and rice"


async def test_ingredient_meal_list_view(module_test_app, module_meal_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_meal_list_view", id=5)
        response = await client.get(path)
        assert response.status_code == 200

        res = response.json()
        result = res["results"]
        assert len(result) == 3

        for r in result:
            assert r["ingredient_name"] == "ham"

        path = app.url_path_for("ingredient_meal_list_view", id=6)
        response = await client.get(path)
        assert response.status_code == 200

        res = response.json()
        result = res["results"]
        assert len(result) == 1

        for r in result:
            assert r["ingredient_name"] == "chickpeas"


@pytest.mark.skip(reason="to do")
async def test_meal_dish_create_view(
    module_test_app, module_transaction, module_meal_data
):
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_dish_update_view(
    module_test_app, module_transaction, module_meal_data
):
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_ingredient_create_view(
    module_test_app, module_transaction, module_meal_data
):
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_ingredient_update_view(
    module_test_app, module_transaction, module_meal_data
):
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_dish_create_view_409():
    # create on missing meal or dish
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_dish_update_view_409():
    # update on missing dish
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_ingredient_create_view_409():
    # create on missing meal or dish
    ...


@pytest.mark.skip(reason="to do")
async def test_meal_ingredient_update_view_409():
    # update on missing ingredient
    ...
