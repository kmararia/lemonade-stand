"""
Settings for home-page layout
"""

import dash
from dash import dcc
from dash import html

from lemonade_stand.app_config import WebConfigs

# Set up page layout
layout = html.Div(
    children=[
        html.Div(id="home-page"),
        html.Div(
            className="home-header",
            children=[
                html.P(children="🍋", className="header-emoji"),
                html.H1(
                    children=html.H1("Lemonade Stand", className="title-button"),
                    className="header-title",
                ),
                html.P(
                    children="A web application to monitor your personal expenditure",
                    className="header-description",
                ),
            ],
        ),
        html.Div(
            className="ripple-container",
            children=[
                html.Div(className="ripple-loader"),
            ],
        ),
        html.Div(
            className="image-menu",
            children=[
                html.Div(
                    className="image-container",
                    children=[
                        dcc.Link(
                            html.Button("Income", className="image-button"),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Img(
                                src=WebConfigs.img_income,
                                className="image-option",
                            ),
                            href="/income",
                        ),
                    ],
                ),
                html.Div(
                    className="image-container",
                    children=[
                        dcc.Link(
                            html.Button("Savings", className="image-button"),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Img(
                                src=WebConfigs.img_savings,
                                className="image-option",
                            ),
                            href="/income",
                        ),
                    ],
                ),
                html.Div(
                    className="image-container",
                    children=[
                        dcc.Link(
                            html.Button("Expenses", className="image-button"),
                            href="/expenses",
                        ),
                        dcc.Link(
                            html.Img(
                                src=WebConfigs.img_expenses,
                                className="image-option",
                            ),
                            href="/expenses",
                        ),
                    ],
                ),
            ],
        ),
    ]
)


# Register page
dash.register_page(__name__, path="/", name="Home", title="Lemonade Stand")
