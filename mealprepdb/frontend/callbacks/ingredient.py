from dash import html, callback, Output, Input, ctx
import httpx
from typing import Dict, Any, List
from dash.exceptions import PreventUpdate
from mealprepdb.config import BASE_BACKEND_URL
from . import common
import datetime


# XXX need error handling for this..PreventUpdate aint no good
def get_ingredients() -> List[Dict[str, Any]]:
    url = f"{BASE_BACKEND_URL}/ingredient/"
    res = httpx.get(url)
    if res.status_code != 200:
        raise PreventUpdate
    res = res.json()
    result = [{"label": i["name"], "value": i["id"]} for i in res["results"]]
    return result


def get_ingredients_in_inventory() -> List[Dict[str, Any]]:
    url = f"{BASE_BACKEND_URL}/ingredient/inventory/"
    res = httpx.get(url)
    if res.status_code != 200:
        raise PreventUpdate
    res = res.json()
    return res["results"]


@callback(
    Output("ingredient_ls", "options"),
    Input("refresh-ingredient", "n_clicks"),
)
def ingredient_dropdown_cb(refresh_bttn):
    if "refresh-ingredient" == ctx.triggered_id:
        return get_ingredients()
    return get_ingredients()


@callback(
    Output("ingredient-create-message", "children"),
    Input("ingredient_name", "value"),
    Input("ingredient_type", "value"),
    Input("create-ingredient-btn", "n_clicks"),
)
def create_ingredient_cb(ingredient_name, ingredient_type, create_button):
    data = {"name": ingredient_name}
    if ingredient_type:
        data["type"] = ingredient_type
    msg = ""
    url = f"{BASE_BACKEND_URL}/ingredient/"
    if "create-ingredient-btn" == ctx.triggered_id:
        common.create(url, data)
        msg = f"{ingredient_name} has been created"

    return html.Div(msg)


@callback(
    Output("inventory-create-message", "children"),
    Input("ingredient_ls", "value"),
    Input("ing_in_inv_from_where", "value"),
    Input("ing_in_inv_brand", "value"),
    Input("ing_in_inv_price", "value"),
    Input("ing_in_inv_quantity", "value"),
    Input("ing_in_inv_unit", "value"),
    Input("ing_in_inv_purchased_on", "date"),
    Input("ing_in_inv_finished_on", "date"),
    Input("create-ingredient-in-inventory-btn", "n_clicks"),
)
def create_ingredient_in_inventory_cb(
    ingredient_id: int,
    from_where: str | None = None,
    brand: str | None = None,
    price: float = 0.0,
    quantity: float = 0.0,
    unit: str | None = None,
    purchased_on: datetime.date | None = None,
    finished_on: datetime.date | None = None,
    create_button: Any = None,
):
    data = {
        "ingredient_id": ingredient_id,
        "from_where": from_where,
        "brand": brand,
        "price": price,
        "quantity": quantity,
        "unit": unit,
        "purchased_on": purchased_on,
        "finished_on": finished_on,
    }
    msg = ""
    url = f"{BASE_BACKEND_URL}/ingredient/inventory"
    print(data)
    if "create-ingredient-in-inventory-btn" == ctx.triggered_id:
        res = _create(url, data)
        res = res.json()
        print(res)
        msg = f"ingredient has been added to inventory"

    return html.Div(msg)


@callback(
    Output("ing_in_inv_ls", "data"),
    Input("refresh-ing-in-inv", "n_clicks"),
)
def get_list_of_ingredient_in_inventory_cb(refresh_bttn):
    if "refresh-ing-in-inv" == ctx.triggered_id:
        return get_ingredients_in_inventory()
    return get_ingredients_in_inventory()
