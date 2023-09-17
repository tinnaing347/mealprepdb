import httpx
import pytest

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
