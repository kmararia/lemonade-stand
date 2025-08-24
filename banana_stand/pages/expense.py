"""
Settings for expenses page layout
"""

from datetime import datetime

import dash
import polars as pl
from dash import Input
from dash import Output
from dash import dcc
from dash import html

from banana_stand.data_store import USER_DATA

# Define module variables
CATEGORY_LIST = USER_DATA.expenses["category"].unique().sort().to_list()
MIN_DATE = str(USER_DATA.expenses["date"].min())
MAX_DATE = str(USER_DATA.expenses["date"].max())


# Set up page layout
layout = html.Div(
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
                                for category in CATEGORY_LIST
                            ],
                            value=CATEGORY_LIST[0] if len(CATEGORY_LIST) else None,
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
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                            start_date=MIN_DATE,
                            end_date=MAX_DATE,
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
                        id="expenses-chart",
                        config={"displayModeBar": "hover"},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@dash.callback(
    Output("expenses-chart", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("category-filter", "value"),
)
def update_charts(start_date: str, end_date: str, category):
    """
    Updates the data displayed based on callback inputs
    """

    # Filter the data
    filtered_data_df = USER_DATA.expenses.filter(
        (pl.col("date") >= datetime.strptime(start_date, "%Y-%m-%d"))
        & (pl.col("date") <= datetime.strptime(end_date, "%Y-%m-%d"))
        & (pl.col("category") == category)
    ).sort(["date", "category"])

    return {
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
                "text": "Expenses incurred",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }


# Register page
dash.register_page(
    __name__, path="/expenses", name="Expenses", title="Expenses - Banana Stand"
)
