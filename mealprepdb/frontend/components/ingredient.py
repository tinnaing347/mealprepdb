from dash import html, dcc, dash_table
import datetime

_ingredient_create_div = html.Div(
    id="ingredient-create-content",
    className="grid-container form-box-container",
    children=[
        html.H4("Create an ingredient", style={"text-align": "left"}),
        html.Div(
            className="grid-item",
            children=[
                html.Div(
                    className="forms-button-container",
                    children=[
                        dcc.Input(
                            id="ingredient_name",
                            type="text",
                            placeholder="Ingredient Name",
                            className="form-input",
                            style={
                                "width": "40%",
                                "margin": "5px",
                                # "margin-left": "10px",
                            },
                        ),
                        dcc.Input(
                            id="ingredient_type",
                            type="text",
                            placeholder="Ingredient Type",
                            className="form-input",
                            style={
                                "width": "40%",
                                "margin": "5px",
                            },
                        ),
                        html.Button(
                            "Submit",
                            id="create-ingredient-btn",
                            n_clicks=0,
                            className="button",
                        ),
                    ],
                )
            ],
        ),
        html.Div(id="ingredient-create-message"),
    ],
    # style={"width": "40%"},
)


_ingredient_drop_down = html.Div(
    className="forms-button-container",
    children=[
        dcc.Dropdown(
            id="ingredient_ls",
            placeholder="Select an Ingredient",
        ),
        html.Button(
            "Refresh",
            id="refresh-ingredient",
            n_clicks=0,
            className="button",
        ),
    ],
)

_ingredient_text_forms = [
    dcc.Input(
        id="ing_in_inv_from_where",
        type="text",
        placeholder="Buy from where",
        className="form-input",
    ),
    dcc.Input(
        id="ing_in_inv_brand",
        type="text",
        placeholder="Brand",
        className="form-input",
    ),
    dcc.Input(
        id="ing_in_inv_price",
        type="float",
        placeholder="Cost",
        className="form-input",
    ),
    dcc.Input(
        id="ing_in_inv_quantity",
        type="float",
        placeholder="Quantity",
        className="form-input",
    ),
    dcc.Input(
        id="ing_in_inv_unit",
        type="text",
        placeholder="Quantity Unit",
        className="form-input",
    ),
]

_ingredient_date_purchase = html.Div(
    id="ingredient-date-picker-box",
    className="date-picker",
    children=[
        html.Span("Purchased On:", style={"width": "25%", "margin-top": "10px"}),
        dcc.DatePickerSingle(
            id="ing_in_inv_purchased_on",
            min_date_allowed=datetime.date(1995, 8, 5),
            max_date_allowed=datetime.datetime.now().date()
            + datetime.timedelta(days=1),
            initial_visible_month=datetime.datetime.now().date(),
            date=datetime.datetime.now().date(),
            style={"display": "inline-block", "width": "25%"},
        ),
        html.Span("Finished On:", style={"width": "25%", "margin-top": "10px"}),
        html.Div(
            dcc.DatePickerSingle(
                id="ing_in_inv_finished_on",
                min_date_allowed=datetime.date(1995, 8, 5),
                max_date_allowed=datetime.datetime.now().date()
                + datetime.timedelta(days=1),
                initial_visible_month=datetime.datetime.now().date(),
                date=datetime.datetime.now().date(),
                # style={"display": "inline-block", "width": "25%"},
            ),
            style={"display": "inline-block", "width": "25%"},
        ),
    ],
)

# XXX need to add assets and refactor css later..what a fucking mess
_ingredient_in_inventory_div = html.Div(
    id="ingredient-in-inventory-create-content",
    className="grid-container form-box-container",
    children=[
        html.H4("Add an ingredient to an inventory", style={"text-align": "left"}),
        html.Div(
            className="grid-item",
            children=[
                _ingredient_drop_down,
                *_ingredient_text_forms,
                _ingredient_date_purchase,
                html.Button(
                    "Submit",
                    id="create-ingredient-in-inventory-btn",
                    n_clicks=0,
                    className="button",
                ),
            ],
        ),
        html.Div(id="inventory-create-message"),
    ],
)


_ingredient_side_form = html.Div(
    id="ingredient-side-form",
    className="side-form",
    children=[
        _ingredient_create_div,
        _ingredient_in_inventory_div,
    ],
)

_ingredient_table = html.Div(
    className="ingredient-table",
    children=[
        html.Label("Ingredient in Inventory"),
        html.Button(
            "Refresh",
            id="refresh-ing-in-inv",
            n_clicks=0,
            className="button",
        ),
        dash_table.DataTable(
            columns=[
                {"name": i, "id": i}
                for i in [
                    "name",
                    "quantity",
                    "unit",
                    "from_where",
                    "brand",
                    "price",
                    "purchased_on",
                    "finished_on",
                ]
            ],
            id="ing_in_inv_ls",
            style_table={"width": "auto"},
            style_cell={"textAlign": "center"},
        ),
    ],
)

ingredient_layout = html.Div(
    id="ingredient-main-content",
    className="main-content",
    children=[
        _ingredient_side_form,
        _ingredient_table,
    ],
    style={"margin-top": "30px", "margin-left": "30px"},
)
