from dash import Dash, html, dcc
from .components import ingredient_layout, dish_layout, meal_layout
from .callbacks import *


app = Dash(external_stylesheets=[])

BASE_URL = "http://api:8080"

app.layout = html.Div(
    children=[
        html.H1(children="MealPrepDB", style={"textAlign": "left"}),
        dcc.Tabs(
            id="tabs-example-graph",
            children=[
                dcc.Tab(
                    label="Ingredient",
                    children=ingredient_layout,
                ),
                dcc.Tab(label="Dish", children=dish_layout),
                dcc.Tab(label="Meal", children=meal_layout),
            ],
            # vertical=True,
            style={
                "float": "left",
                "height": "50px",
                "width": "50%",
            },
        ),
    ]
)


server = app.server
