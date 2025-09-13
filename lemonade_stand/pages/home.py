"""
Settings for home-page layout
"""

import dash
from dash import dcc
from dash import html

# Set up page layout
layout = html.Div(
    children=[
        html.Div(id="home-page"),
        html.Div(
            children=[
                html.P(children="🍌", className="header-emoji"),
                html.H1(
                    children=html.H1("Lemonade-stand App", className="title-button"),
                    className="header-title",
                ),
                html.P(
                    children="A web application to monitor your personal expenditure",
                    className="header-description",
                ),
            ],
            className="home-header",
        ),
        html.Div(
            children=[
                html.Div(className="ripple-loader"),
            ],
            className="ripple-container",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Link(
                            html.Button("Income", className="image-button"),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Img(
                                src="/assets/images/income2.jpg",
                                className="image-option",
                            ),
                            href="/income",
                        ),
                    ],
                    className="image-container",
                ),
                html.Div(
                    children=[
                        dcc.Link(
                            html.Button("Savings", className="image-button"),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Img(
                                src="/assets/images/savings2.jpg",
                                className="image-option",
                            ),
                            href="/income",
                        ),
                    ],
                    className="image-container",
                ),
                html.Div(
                    children=[
                        dcc.Link(
                            html.Button("Expenses", className="image-button"),
                            href="/expenses",
                        ),
                        dcc.Link(
                            html.Img(
                                src="/assets/images/expenses2.jpg",
                                className="image-option",
                            ),
                            href="/expenses",
                        ),
                    ],
                    className="image-container",
                ),
            ],
            className="image-menu",
        ),
    ]
)


# Register page
dash.register_page(__name__, path="/", name="Home", title="Banana Stand")
