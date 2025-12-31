"""
Income page layout configurations
"""

from datetime import datetime
from pathlib import Path

import polars as pl
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shinywidgets import output_widget
from shinywidgets import render_widget

from lemonade_stand.shiny.shared import build_bar_chart
from lemonade_stand.shiny.shared import build_line_chart
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def income_ui():
    """
    A UI module for the income page
    """

    return ui.nav_panel(
        "Income",
        # Data distribution container
        ui.tags.div(
            ui.div(
                ui.h3("Transaction Summary", style="font-weight: bold; width: 100%"),
                ui.div(
                    ui.input_date_range(
                        id="daterange_select",
                        label=None,
                        format="mm/dd/yyyy",
                        separator="→",
                        width="100%",
                    ),
                    ui.input_select(
                        id="graph_type",
                        label=None,
                        choices={"bar": "bar graph", "line": "line graph"},
                        selected="bar",
                        width="50%",
                    ),
                    style="display: flex; justify-content: flex-end; align-items: flex-end;  gap: 20px;",
                ),
                style="display: flex; justify-content: space-between; align-items: center;",
            ),
            ui.br(),
            output_widget("plot_data"),
            id="plot-container",
        ),
        ui.br(),
        ui.br(),
        # Data container
        ui.tags.div(
            ui.div(
                ui.h5("Income", style="font-weight: bold;"),
                ui.download_button(
                    id="download_data", label="Download CSV", class_="download-button"
                ),
                style="display: flex; justify-content: space-between; align-items: center;",
            ),
            ui.output_data_frame("income_data_table"),
            id="table-container",
        ),
        # Add loader spinners
        ui.busy_indicators.options(
            spinner_type="bars", spinner_selector="#plot-container"
        ),
    )


@module.server
def income_server(input, output, session, view_mode_setting, data_df):  # noqa: ARG001
    """
    A server module for the income page
    """

    # Update date selectors
    @reactive.effect
    def _():
        min_max_dates = data_df.select(
            pl.max("date").dt.offset_by("-1y").alias("min"),
            pl.max("date").alias("max"),
        )

        ui.update_date_range(
            "daterange_select",
            start=min_max_dates.item(0, "min"),
            end=min_max_dates.item(0, "max"),
        )

    @reactive.Calc
    def data() -> pl.DataFrame:
        # Filter and summarize the income data
        selected_dates = input.daterange_select()

        clean_df = (
            data_df.filter(
                pl.col("date").is_between(
                    lower_bound=selected_dates[0], upper_bound=selected_dates[1]
                )
            )
            .group_by([pl.col("date"), pl.col("category")])
            .agg(pl.sum("amount").alias("amount"))
        )

        return clean_df

    # Chart logic
    @render_widget  # type: ignore
    def plot_data():
        if not input.daterange_select() or input.graph_type() is None:
            return None

        user_data = data()

        if input.graph_type() == "line":
            return build_line_chart(
                data_df=user_data,
                x_var="date",
                y_var="amount",
                color_var="category",
                view_mode=view_mode_setting(),
            )
        else:
            return build_bar_chart(
                data_df=user_data,
                x_var="date",
                y_var="amount",
                color_var="category",
                view_mode=view_mode_setting(),
            )

    # Table logic
    @render.data_frame
    def income_data_table():
        # Pull dataframe
        data_df: pl.DataFrame = (
            data()
            .group_by(  # type: ignore
                [
                    pl.col("date").dt.truncate("1mo").alias("date_trunc"),
                    pl.col("category"),
                ]
            )
            .agg(pl.sum("amount").alias("amount"))
        )

        # Check if the data spans across multiple years
        year_spans = (
            data_df.select(pl.col("date_trunc").dt.year())
            .unique()
            .to_series()
            .to_list()
        )

        # Pivot the year-months
        pivoted_data = data_df.sort(by=pl.col("date_trunc"), descending=False).pivot(
            on="date_trunc", index="category", values="amount", maintain_order=True
        )

        # Finalize dataset to be dipsl
        final_df = pivoted_data.select(
            pl.col("category").alias(" "),
            *[
                pl.col(x).alias(
                    datetime.strptime(x, "%Y-%m-%d").strftime(
                        "%Y %B"
                        if len(year_spans) > 1
                        else "%B"  # TODO: Future updates to include 2 headers (month and year). Will utilize javascript to set this up
                    )
                )
                for x in pivoted_data.columns
                if x.lower() not in ["category"]
            ],
        )

        return render.DataGrid(
            final_df.to_pandas(),
            height="400px",
            width="100%",
            summary=False,
            editable=False,
        )
