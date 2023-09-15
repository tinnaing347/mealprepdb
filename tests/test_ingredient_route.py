import httpx
import pytest

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
        assert len(results) == 2

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
