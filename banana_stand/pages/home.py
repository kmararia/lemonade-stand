"""
Settings for home-page layout
"""

import dash
from dash import dcc
from dash import html

# Set up page layout
layout = html.Div(
    children=[
        html.Div(
            id="home-page",
            children=[
                html.P(children="🍌", className="header-emoji"),
                html.H1(
                    children="Banana-stand App",
                    className="header-title",
                ),
                html.P(
                    children="A web application to monitor personal expenditure",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Link(
                            html.Img(
                                src="/assets/images/income2.jpg",
                                className="image-option",
                            ),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Button("Income", className="button-85"),
                            href="/income",
                        ),
                    ],
                    className="image-container",
                ),
                html.Div(
                    children=[
                        dcc.Link(
                            html.Img(
                                src="/assets/images/savings2.jpg",
                                className="image-option",
                            ),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Button("Savings", className="button-85"),
                            href="/income",
                        ),
                    ],
                    className="image-container",
                ),
                html.Div(
                    children=[
                        dcc.Link(
                            html.Img(
                                src="/assets/images/expenses2.jpg",
                                className="image-option",
                            ),
                            href="/expenses",
                        ),
                        dcc.Link(
                            html.Button("Expenses", className="button-85"),
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
