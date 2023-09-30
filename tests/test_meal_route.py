import httpx
import pytest

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
