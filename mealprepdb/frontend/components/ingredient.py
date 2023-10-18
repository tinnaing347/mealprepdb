from dash import html, dcc


_ingredient_drop_down = html.Div(
    id="ingredient-dropdown-content",
    children=[
        html.Div(
            dcc.Dropdown(
                id="ingredient_ls",
                placeholder="Select an Ingredient",
                style={
                    "float": "left",
                    "width": "70%",
                    "display": "inline-block",
                    "margin-right": "-150px",
                },
            ),
            id="ingredient_ls_container",
            className="grid-item",
        ),
        html.Div(
            html.Button(
                "Refresh",
                id="refresh-ingredient",
                n_clicks=0,
                style={
                    "width": "10%",
                    "height": "35px",
                },
            ),
            className="grid-item",
        ),
    ],
    style={"width": "40%"},
    className="grid-container",
)

_ingredient_create_div = html.Div(
    id="ingredient-create-content",
    className="grid-container",
    children=[
        html.H4("Create an ingredient"),
        html.Div(
            className="grid-item",
            children=[
                dcc.Input(
                    id="ingredient_name",
                    type="text",
                    placeholder="Ingredient Name",
                    style={
                        "height": "35px",
                        "width": "22.5%",
                        "border-radius": "3px",
                    },
                ),
                dcc.Input(
                    id="ingredient_type",
                    type="text",
                    placeholder="Ingredient Type",
                    style={
                        "margin-left": "16px",
                        "height": "35px",
                        "width": "22.5%",
                        "border-radius": "3px",
                    },
                ),
                html.Button(
                    "Submit",
                    id="create-ingredient-btn",
                    n_clicks=0,
                    style={
                        "margin-left": "17px",
                        "width": "10%",
                        "height": "35px",
                    },
                ),
            ],
            style={"margin-bottom": "20px"},
        ),
        html.Div(id="container-button-timestamp"),
    ],
    style={"width": "40%"},
)

ingredient_layout = html.Div(
    id="ingredient-content",
    children=[
        _ingredient_drop_down,
        _ingredient_create_div,
    ],
    style={"margin-top": "30px", "margin-left": "30px"},
)
