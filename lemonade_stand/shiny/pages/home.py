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
            ui.div(
                ui.h3("Transaction Summary", style="font-weight: bold;"),
                ui.input_selectize(
                    id="year_select",
                    label="Year:",
                    choices=[],
                    multiple=True,
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
                ui.h5("Cash flow history", style="font-weight: bold;"),
                ui.download_button(
                    "download_data", "Download CSV", class_="download-button"
                ),
                style="display: flex; justify-content: space-between; align-items: center;",
            ),
            ui.output_data_frame("table_data"),
            id="table-container",
        ),
        # Add loader spinners
        ui.busy_indicators.options(
            spinner_type="bars", spinner_selector="#plot-container"
        ),
    )


@module.server
def home_server(input, output, session, view_mode_setting, data_df):  # noqa: ARG001
    """
    A UI module for the home page
    """

    # Update Year selectors
    @reactive.effect
    def _():
        year_choices = (
            data_df.select(pl.col("date").dt.year().unique())
            .sort(by="date", descending=True)
            .get_column("date")
            .to_list()
        )

        ui.update_select(
            "year_select",
            choices=year_choices,
            selected=year_choices[0],
        )

    @reactive.Calc
    def data():
        # Filter and clean up the data
        clean_df = (
            data_df.filter(
                pl.col("date").dt.year().cast(pl.String).is_in(input.year_select())
            )
            .sort(by="date", descending=True)  # Sort from latest to oldest
            .rename(lambda col: col.capitalize())  # Rename the columns for consistency
        )

        return clean_df.to_pandas()

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
            x="Date",
            y="Amount",
            color="Type",
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
            title="<b>Cash Flow Over Years<b>",
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
    def table_data():
        # Pull dataframe
        data_df = data()

        return render.DataGrid(
            data_df.assign(
                Date=data_df["Date"].dt.strftime("%B %d, %Y")
            ),  # Convert dates to the appropriate format
            height="400px",
            width="100%",
            filters=True,
            summary=False,
            # editable=True,
        )

    # Download the data
    @render.download(filename="transactions.csv")
    def download_data():
        # Yield a function that writes to the file path Shiny provides
        yield data().to_csv(index=False)
