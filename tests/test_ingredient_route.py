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
