"""
Income page layout configurations
"""

from datetime import datetime

import dash
import polars as pl
from dash import Input
from dash import Output
from dash import dcc
from dash import html

from lemonade_stand.data import USER_DATA

# Define module variables
CATEGORY_LIST = USER_DATA.income["category"].unique().sort().to_list()
SOURCE_LIST = USER_DATA.income["source"].unique().sort().to_list() + ["All - Selected"]
MIN_DATE = str(USER_DATA.income["date"].min())
MAX_DATE = str(USER_DATA.income["date"].max())


# Set up page layout
layout = html.Div(
    children=[
        html.Div(id="dummy-output"),
        html.Button("⬅ Back", id="back-button"),
        html.Div(
            className="side-panel",
            children=[
                html.Div(
                    className="hamburger",
                    children=[html.Span() for _ in range(3)],
                ),
                html.Div(
                    className="panel-content",
                    children=[
                        html.H2("Dashboard Menu"),
                        dcc.Link(
                            html.Button("Home", className="panel-button"),
                            href="/",
                        ),
                        dcc.Link(
                            html.Button("Income", className="panel-button"),
                            href="/income",
                        ),
                        dcc.Link(
                            html.Button("Savings", className="panel-button"),
                            href="/savings",
                        ),
                        dcc.Link(
                            html.Button("Expenses", className="panel-button"),
                            href="/expenses",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="header",
            children=[
                html.P(children="🍋", className="header-emoji"),
                html.H1(
                    children=html.H1("Lemonade-stand App", className="title-button"),
                    className="header-title",
                ),
                html.P(
                    children="A web application to monitor your personal expenditure",
                    className="header-description",
                ),
            ],
        ),
        html.Div(
            className="menu",
            children=[
                html.Div(
                    children=[
                        html.Div(children="Source", className="menu-title"),
                        dcc.Dropdown(
                            id="source-filter",
                            options=[
                                {"label": source, "value": source}
                                for source in SOURCE_LIST
                            ],
                            value="All - Selected",
                            clearable=False,
                            searchable=True,
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Category", className="menu-title"),
                        dcc.Dropdown(
                            id="category-filter",
                            options=[
                                {"label": category, "value": category}
                                for category in CATEGORY_LIST
                            ],
                            value=CATEGORY_LIST[0] if len(CATEGORY_LIST) else None,
                            clearable=False,
                            searchable=True,
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            className="menu-title",
                            children="Date range",
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            className="date-bar",
                            display_format="MMM D, YYYY",
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                            start_date=MIN_DATE,
                            end_date=MAX_DATE,
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            className="glow-container",
            children=[
                html.Div(
                    className="box",
                    children=dcc.Graph(
                        id="income-chart",
                        config={"displayModeBar": "hover"},
                    ),
                ),
            ],
        ),
    ]
)


dash.clientside_callback(
    """
    function(n_clicks) {
        if(n_clicks > 0) {
            window.history.back();
        }
        return "";
    }
    """,
    dash.Output("dummy-output", "children"),
    dash.Input("back-button", "n_clicks"),
)


@dash.callback(
    Output("income-chart", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("category-filter", "value"),
    Input("source-filter", "value"),
)
def update_charts(start_date: str, end_date: str, category: str, source: str):
    """
    Updates the data displayed based on callback inputs
    """

    # Filter the data
    filtered_data_df = USER_DATA.income.filter(
        (pl.col("date") >= datetime.strptime(start_date, "%Y-%m-%d"))
        & (pl.col("date") <= datetime.strptime(end_date, "%Y-%m-%d"))
        & (pl.col("category") == category)
        & ((pl.col("source") == source) if source != "All - Selected" else pl.lit(True))
    ).sort(["date", "category"])

    # Summarize data
    filtered_data_df = filtered_data_df.group_by("date").agg(
        pl.col("amount").sum().alias("amount")
    )

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
                "text": "Income received",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
            "plot_bgcolor": "#181818",
            "paper_bgcolor": "#181818",
            "font": {"color": "#e0e0e0"},
        },
    }


# Register page
dash.register_page(
    __name__, path="/income", name="Income", title="Income - Lemonade Stand"
)
