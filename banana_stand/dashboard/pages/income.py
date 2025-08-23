"""
Income amounts bar graph
"""

from datetime import datetime

import polars as pl
from dash import Dash
from dash import Input
from dash import Output
from dash import dcc
from dash import html


def add_income_layout(app: Dash, data_df: pl.DataFrame):
    """
    Styles the income bar graph summary for the application
    """

    # Define variables
    category_list = data_df["category"].unique().sort().to_list()
    min_date = str(data_df["date"].min())
    max_date = str(data_df["date"].max())

    # Set up application layouts
    app.title = "Banana-Stand Analytics"

    app.layout = html.Div(
        children=[
            html.Div(
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
                            html.Div(children="Type", className="menu-title"),
                            dcc.Dropdown(
                                id="category-filter",
                                options=[
                                    {"label": category, "value": category}
                                    for category in category_list
                                ],
                                value=category_list[0] if len(category_list) else None,
                                clearable=False,
                                searchable=True,
                                className="dropdown",
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                children="Date Range",
                                className="menu-title",
                            ),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=max_date,
                            ),
                        ]
                    ),
                ],
                className="menu",
            ),
            html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(
                            id="income-chart",
                            config={"displayModeBar": "hover"},
                        ),
                        className="card",
                    ),
                ],
                className="wrapper",
            ),
        ]
    )

    @app.callback(
        Output("income-chart", "figure"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("category-filter", "value"),
    )
    def update_charts(start_date: str, end_date: str, category):
        """ """

        # Filter the data
        filtered_data_df = data_df.filter(
            (pl.col("date") >= datetime.strptime(start_date, "%Y-%m-%d"))
            & (pl.col("date") <= datetime.strptime(end_date, "%Y-%m-%d"))
            & (pl.col("category") == category)
        ).sort(["date", "category"])

        # Update the chart figure
        chart_figure = {
            "data": [
                {
                    "x": filtered_data_df["date"].to_list(),
                    "y": filtered_data_df["amount"].to_list(),
                    "type": "bar",
                    "hovertemplate": "$%{y:.2f}<extra></extra>",
                },
            ],
            "layout": {
                "title": {
                    "text": "Income received",
                    "x": 0.05,
                    "xanchor": "left",
                },
                "xaxis": {"fixedrange": True},
                "yaxis": {"tickprefix": "$", "fixedrange": True},
                "colorway": ["#17B897"],
            },
        }

        return chart_figure

    return app
