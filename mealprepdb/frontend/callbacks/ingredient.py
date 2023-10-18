from dash import html, callback, Output, Input, ctx
import httpx
from typing import Dict, Any, List
from dash.exceptions import PreventUpdate
from mealprepdb.config import BASE_BACKEND_URL


# XXX need error handling for this..PreventUpdate aint no good
def get_ingredients() -> List[Dict[str, Any]]:
    url = f"{BASE_BACKEND_URL}/ingredient/"
    res = httpx.get(url)
    if res.status_code != 200:
        raise PreventUpdate
    res = res.json()
    result = [i["name"] for i in res["results"]]
    return result


def _create(url: str, data: Dict[str, Any]):
    res = httpx.post(url, json=data)
    if res.status_code != 201:
        raise PreventUpdate
    return res


@callback(
    Output("ingredient_ls", "options"),
    Input("refresh-ingredient", "n_clicks"),
)
def ingredient_dropdown_cb(refresh_bttn):
    if "refresh-ingredient" == ctx.triggered_id:
        return get_ingredients()
    return get_ingredients()


@callback(
    Output("container-button-timestamp", "children"),
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
        _create(url, data)
        msg = f"{ingredient_name} has been created"

    return html.Div(msg)
