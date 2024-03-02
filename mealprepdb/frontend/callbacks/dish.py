from dash import html, callback, Output, Input, ctx
from typing import List, Dict, Any
import httpx
from dash.exceptions import PreventUpdate
from mealprepdb.config import BASE_BACKEND_URL
import datetime
from . import common


def get_parent_dish() -> List[Dict[str, Any]]:
    url = f"{BASE_BACKEND_URL}/dish/"

    # only show things that has been created within 10 days window
    # otherwise you know food poisioning and what not haha
    date_le = datetime.datetime.now()
    date_ge = date_le - datetime.timedelta(days=10)
    res = httpx.get(
        url,
        params={
            "created_on__le": date_le.strftime("%Y-%m-%d"),
            "created_on__ge": date_ge.strftime("%Y-%m-%d"),
        },
    )
    if res.status_code != 200:
        raise PreventUpdate
    res = res.json()
    result = [
        {"label": f"{i['name']} - {i['created_on']}", "value": i["id"]}
        for i in res["results"]
    ]
    return result


@callback(
    Output("parent_dish_ls", "options"),
    Input("refresh-parent-dish", "n_clicks"),
)
def dish_dropdown_cb(refresh_bttn):
    if "refresh-parent-dish" == ctx.triggered_id:
        return get_parent_dish()
    return get_parent_dish()


@callback(
    Output("dish-create-message", "children"),
    Input("dish_name", "value"),
    Input("parent_dish_ls", "value"),
    Input("dish_created_on", "date"),
    Input("create-dish-btn", "n_clicks"),
)
def create_dish_cb(dish_name, parent_dish_id, dish_created_on, create_button):
    data = {"name": dish_name, "created_on": dish_created_on}
    if parent_dish_id:
        data["parent_dish_id"] = parent_dish_id
    msg = ""
    url = f"{BASE_BACKEND_URL}/dish/"
    if "create-dish-btn" == ctx.triggered_id:
        common.create(url, data)
        msg = f"A dish: {dish_name} has been created"

    return html.Div(msg)
