import httpx
from typing import Dict, Any
from dash.exceptions import PreventUpdate


def create(url: str, data: Dict[str, Any]):
    res = httpx.post(url, json=data)
    if res.status_code != 201:
        raise PreventUpdate
    return res
