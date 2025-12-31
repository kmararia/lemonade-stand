"""
Income page layout configurations
"""

from datetime import datetime
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
def income_ui():
    """
    A UI module for the income page
    """

    return ui.nav_panel(
        "Income",
        # Data distribution container
        ui.tags.div(
            ui.div(
                ui.h3("Transaction Summary", style="font-weight: bold;"),
                ui.input_selectize(
                    id="graph_select",
                    label="Graph:",
                    choices=["line graph", "bar graph"],
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

    @reactive.Calc
    def data():
        # Prepare the used dataset
        clean_df = (
            data_df
            # .filter(
            #     pl.col("date").is_between(
            #         pl.lit("2024-01-01").str.to_date(),
            #         pl.lit("2024-12-01").str.to_date(),
            #     )
            # )
            .group_by([pl.col("date"), pl.col("category")]).agg(
                pl.sum("amount").alias("amount")
            )
        )

        return clean_df

    # Chart logic
    @render_widget  # type: ignore
    def plot_data():
        # Set theme-specific colors
        if view_mode_setting() == "light":
            theme = "plotly_white"
            font_color = "black"
            hover_bg_color = "white"

        else:
            theme = "plotly_dark"
            font_color = "white"
            hover_bg_color = "#333"

        # Create the figure
        fig = px.line(
            data_frame=data(),
            x="date",
            y="amount",
            color="category",
            template=theme,
        )

        # Update the x-axis vertical line
        fig.update_xaxes(
            showspikes=True,
            spikemode="across",
            spikecolor="#f91414",
            spikethickness=1,
            spikedash="solid",
            showline=True,
        )

        # Fine-tune the the plot layout
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b>: $%{y:.2f}<extra></extra>"
        )

        fig.update_layout(
            title="<b>Cash Flow by Category<b>",
            title_x=0.5,
            font_color=font_color,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"l": 0, "r": 0, "t": 40, "b": 0},
            hovermode="x unified",
            hoverlabel={
                "bgcolor": hover_bg_color,
                "bordercolor": "black",
            },
            xaxis={
                "title_text": "Date",
                "hoverformat": "<b>%A, %B %d, %Y<b>",
                "tickformat": "%b %Y",
                "nticks": 10,
                "tickangle": 0,
                "dtick": "M2",
            },
            yaxis={"title_text": "Amount (USD)", "tickprefix": "$"},
        )

        return fig

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
