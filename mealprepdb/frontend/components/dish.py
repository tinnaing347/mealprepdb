from dash import html, dcc
from dash import html, dcc, dash_table
import datetime


_parent_dish_drop_down = html.Div(
    className="forms-button-container",
    children=[
        dcc.Dropdown(
            id="parent_dish_ls",
            placeholder="Select a dish",
        ),
        html.Button(
            "Refresh",
            id="refresh-parent-dish",
            n_clicks=0,
            className="button",
        ),
    ],
)

_dish_date_created = html.Div(
    id="dish-date-picker-box1",
    className="date-picker",
    children=[
        html.Span("Created On:", style={"width": "25%", "margin-top": "10px"}),
        dcc.DatePickerSingle(
            id="dish_created_on",
            min_date_allowed=datetime.date(1995, 8, 5),
            max_date_allowed=datetime.datetime.now().date()
            + datetime.timedelta(days=1),
            initial_visible_month=datetime.datetime.now().date(),
            date=datetime.datetime.now().date(),
            style={"display": "inline-block", "width": "25%"},
        ),
    ],
)

_dish_create_div = html.Div(
    id="dish-create-content",
    className="grid-container form-box-container",
    children=[
        html.H4("Add a new dish", style={"text-align": "left"}),
        html.Div(
            className="grid-item",
            children=[
                _parent_dish_drop_down,
                dcc.Input(
                    id="dish_name",
                    type="text",
                    placeholder="Dish Name",
                    className="form-input",
                ),
                _dish_date_created,
                html.Button(
                    "Submit",
                    id="create-dish-btn",
                    n_clicks=0,
                    className="button",
                ),
            ],
        ),
        html.Div(id="dish-create-message"),
    ],
)


_dish_side_form = html.Div(
    className="side-form",
    children=[
        _dish_create_div,
    ],
)

dish_layout = html.Div(
    id="dish-main-content",
    className="main-content",
    children=[
        _dish_side_form,
    ],
    style={"margin-top": "30px", "margin-left": "30px"},
)
