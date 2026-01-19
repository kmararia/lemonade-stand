"""
Settings for home-page layout
"""

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
def home_ui():
    """
    A UI module for the home page
    """

    return ui.nav_panel(
        "Home",
        # Data plot container
        ui.tags.div(
            ui.div(
                ui.h4("Transaction Summary"),
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
                style="display: flex; justify-content: space-between; align-items: center; width: 100%;",
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
                ui.h5("Cash flow history"),
                ui.download_button(
                    "download_data", "Download CSV", class_="download-button"
                ),
                style="display: flex; justify-content: space-between; align-items: center;",
            ),
            ui.output_data_frame("home_data_table"),
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
        # Filter and clean up the data
        selected_dates = input.daterange_select()

        clean_df = (
            data_df.filter(
                pl.col("date").is_between(
                    lower_bound=selected_dates[0], upper_bound=selected_dates[1]
                )
            )
            .sort(by="date", descending=True)  # Sort from latest to oldest
            .rename(lambda col: col.capitalize())  # Rename the columns for consistency
        )

        return clean_df.to_pandas()

    # Chart logic
    @render_widget  # type: ignore
    def plot_data():
        if not input.daterange_select() or input.graph_type() is None:
            return None

        user_data = data()

        if input.graph_type() == "line":
            return build_line_chart(
                data_df=user_data,
                x_var="Date",
                y_var="Amount",
                color_var="Type",
                view_mode=view_mode_setting(),
            )
        else:
            return build_bar_chart(
                data_df=user_data,
                x_var="Date",
                y_var="Amount",
                color_var="Type",
                view_mode=view_mode_setting(),
            )

    # Table logic
    @render.data_frame
    def home_data_table():
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
