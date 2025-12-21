"""
Settings for home-page layout
"""

from pathlib import Path

import plotly.express as px
import polars as pl
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shinywidgets import output_widget
from shinywidgets import render_widget

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def home_ui():
    """
    A UI module for the home page
    """

    return ui.nav_panel(
        "Home",
        # Data distribution container
        ui.tags.div(
            ui.h3("Transaction Data"),
            output_widget("data_points"),
            id="plot-container",
        ),
        # Data container
        ui.tags.div(
            # ui.input_select(id="year-label", label="Year:", choices=["N/A"]),
            ui.output_data_frame("table_data"),
            id="table-container",
        ),
    )


@module.server
def home_server(input, output, session, data_df):  # noqa: ARG001
    """
    A UI module for the home page
    """

    @reactive.Calc
    def data():
        # Stack all the datasets within the set timeframe
        stacked_df = pl.union(
            [
                data_df.income,
                data_df.savings,
                data_df.expenses,
                data_df.unknown,
            ],
            how="diagonal",
        )

        # Clean up the data
        stacked_df = (
            stacked_df.sort(by="date", descending=True)  # Sort from latest to oldest
            .with_columns(
                pl.col("date").dt.strftime("%B %d, %Y").alias("date")
            )  # Update to a prettier date-format
            .rename(lambda col: col.capitalize())  # Rename the columns for consistency
        )

        return stacked_df.to_pandas()

    # Chart logic
    @render_widget  # type: ignore
    def iris_plot():
        fig = px.line(
            data(),
            x="Date",
            y="Amount",
            color="Category",
            title="Life Expectancy in Oceania",
        )

        # Improve layout responsiveness
        fig.update_layout(margin={"l": 0, "r": 0, "t": 40, "b": 0})

        return fig

    # Table logic
    @render.data_frame
    def table_data():
        return render.DataGrid(data(), height="400px", width="100%")
