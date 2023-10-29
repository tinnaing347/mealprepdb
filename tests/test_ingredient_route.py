import httpx
import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.anyio


async def test_ingredient_list_view(module_test_app, module_ingredient_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_list_view")
        response = await client.get(path)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) > 0

        params = {"type": "seeds"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 0

        params = {"type": "spice"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1

        params = {"name__contains": "ri"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1

        params = {"name": "onion"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1


async def test_ingredient_detail_view(module_test_app, module_ingredient_data):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_detail_view", id=1)
        response = await client.get(path)
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "onion"

        path = app.url_path_for("ingredient_detail_view", id=42)
        response = await client.get(path)
        assert response.status_code == 404


async def test_ingredient_in_inventory_list_view(
    module_test_app, module_ingredient_data
):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_in_inventory_list_view")
        response = await client.get(path)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) > 0

        params = {"name": "onion"}
        response = await client.get(path, params=params)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 2

        res = results[0]
        assert res["name"] == "onion"

        params = {"purchased_on__le": "2017-07-02"}
        response = await client.get(path, params=params)
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 5

        params = {"finished_on": "2017-07-02"}
        response = await client.get(path, params=params)
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 0

        params = {"finished_on": "2017-07-01"}
        response = await client.get(path, params=params)
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1

        params = {"finished_on": "2017-00-01"}
        response = await client.get(path, params=params)
        assert response.status_code == 422

        params = {"from_where": "leek ville"}
        response = await client.get(path, params=params)
        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) == 1


async def test_ingredient_in_inventory_detail_view(
    module_test_app, module_ingredient_data
):
    app = module_test_app
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_in_inventory_detail_view", id=1)
        response = await client.get(path)
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "onion"
        assert result["from_where"] == "onion ville"

        path = app.url_path_for("ingredient_in_inventory_detail_view", id=42)
        response = await client.get(path)
        assert response.status_code == 404


async def test_ingredient_create_view(
    module_test_app, module_transaction, module_ingredient_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_create_view")
        data = {"name": "carrot", "type": "vegetable"}
        response = await client.post(path, json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["name"] == "carrot"

        # clean up
        t = transaction.get_table("ingredient")
        stmt = sa.delete(t).where(t.c.id == result["id"]).returning(t)
        res = await transaction.execute(stmt)
        obj_ = res.one()
        assert obj_.id == result["id"]


async def test_ingredient_update_view(
    module_test_app, module_transaction, module_ingredient_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_detail_view", id=1)
        res = await client.get(path)
        res = res.json()
        assert res["type"] == "base_vegetable"

        path = app.url_path_for("ingredient_update_view", id=1)
        data = {"type": "vegetable"}
        response = await client.put(path, json=data)
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "onion"
        assert result["type"] == "vegetable"


async def test_ingredient_in_inventory_create_view(
    module_test_app, module_transaction, module_ingredient_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_in_inventory_create_view")
        data = {
            "ingredient_id": 1,
            "from_where": "onion ville",
            "brand": "",
            "price": 4.2,
            "quantity": 4.2,
            "unit": "pound",
            "purchased_on": "2017-07-10",
        }
        # buy more onion and keep everyone away
        response = await client.post(path, json=data)
        assert response.status_code == 201

        result = response.json()
        assert result["ingredient_id"] == 1
        assert result["price"] == 4.2
        assert result["quantity"] == 4.2
        assert result["purchased_on"] == "2017-07-10"
        assert result["finished_on"] == None

        # clean up
        t = transaction.get_table("ingredient_in_inventory")
        stmt = sa.delete(t).where(t.c.id == result["id"]).returning(t)
        res = await transaction.execute(stmt)
        obj_ = res.one()
        assert obj_.id == result["id"]


async def test_ingredient_update_view(
    module_test_app, module_transaction, module_ingredient_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_in_inventory_detail_view", id=1)
        res = await client.get(path)
        res = res.json()
        assert res["from_where"] == "onion ville"
        assert res["price"] == 3.5
        assert res["unit"] == "pound"

        path = app.url_path_for("ingredient_in_inventory_update_view", id=1)
        data = {"from_where": "garlic ville"}
        response = await client.put(path, json=data)
        assert response.status_code == 200

        res = response.json()
        assert res["from_where"] == "garlic ville"
        assert res["price"] == 3.5
        assert res["unit"] == "pound"


async def test_ingredient_create_view_409(
    module_test_app, module_transaction, module_ingredient_data
):
    app = module_test_app
    transaction = module_transaction
    async with httpx.AsyncClient(app=app, base_url="https://fake.com") as client:
        path = app.url_path_for("ingredient_create_view")
        data = {"name": "onion"}
        response = await client.post(path, json=data)
        assert response.status_code == 409

        await transaction.rollback()


@pytest.mark.skip(reason="to do")
async def test_ingredient_in_inventory_create_view_409():
    # create on missing non existent ingredient
    ...


@pytest.mark.skip(reason="to do")
async def test_ingredient_in_inventory_update_view_409():
    # update on missing non existent ingredient
    ...
