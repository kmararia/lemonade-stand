"""
Income page layout configurations
"""

from pathlib import Path

import polars as pl
from great_tables import GT
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
                ui.output_ui(id="total_income"),
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
                    class_="items-bottom-right",
                ),
                class_="items-space-between",
            ),
            output_widget("plot_data"),
            id="plot-container",
        ),
        # Data container
        ui.div(
            ui.h5("Income"),
            ui.download_button(
                id="download_data", label="Download CSV", class_="download-button"
            ),
            class_="items-space-between",
        ),
        ui.output_ui("income_data_table"),
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

    # Total income render
    @render.ui
    def total_income():
        summ_income = data().select(pl.sum("amount").alias("amount")).item(0, "amount")

        if summ_income >= 0:
            amount_css_class = "positive-amounts"
            dollar_sign = "$"
        else:
            amount_css_class = "negative-amounts"
            dollar_sign = "$-"

        return ui.h4(
            ui.p(
                ui.span(
                    dollar_sign, style="font-family: Courier New; font-weight: bold;"
                ),
                ui.span(f"{abs(summ_income):,.0f}"),
                class_=amount_css_class,
            ),
            ui.p(
                "earned this period",
                style="font-size: 0.9rem; font-style: italic; margin-left: 0.9rem;",
            ),
        )

    # Chart logic
    @render_widget  # type: ignore
    def plot_data():
        """"""

        if not input.daterange_select() or input.graph_type() is None:
            return None

        user_data = data()
        user_data = user_data.rename({x: x.capitalize() for x in user_data.columns})

        if input.graph_type() == "line":
            return build_line_chart(
                data_df=user_data,
                x_var="Date",
                y_var="Amount",
                color_var="Category",
                view_mode=view_mode_setting(),
            )
        else:
            return build_bar_chart(
                data_df=user_data,
                x_var="Date",
                y_var="Amount",
                color_var="Category",
                view_mode=view_mode_setting(),
            )

    @reactive.Calc
    def pivot_data() -> pl.DataFrame:
        """"""

        summ_df = (
            data()
            .group_by(
                [
                    pl.col("date").dt.strftime("%Y_%B").alias("date_trunc"),
                    pl.col("category"),
                ]
            )
            .agg(pl.sum("amount").alias("amount"))
            .sort(by=pl.col("date_trunc"), descending=False)
        )

        return summ_df.pivot(
            on="date_trunc", index="category", values="amount", maintain_order=True
        )

    @render.ui
    def income_data_table():
        """"""

        # Initialize variables
        data_df = pivot_data()
        return_obj = GT(data_df)
        map_col_month = {}
        map_year_col = {}

        # Iterate through columns and group them by year
        for x in data_df.columns:
            if x.lower() in ["category"]:
                map_col_month[x] = ""
            else:
                field_year, field_month = x.split("_")
                map_col_month[x] = field_month
                map_year_col[field_year] = map_year_col.get(field_year, []) + [x]

        # Iterate through the mappings and create headers
        for field_year, month_list in map_year_col.items():
            return_obj = return_obj.tab_spanner(label=field_year, columns=month_list)

        return ui.HTML(
            return_obj.cols_label(cases=None, **map_col_month)
            .tab_options(
                table_background_color="transparent",
                column_labels_background_color="transparent",
                table_font_color="#f8f9fa",
                table_width="100%",
            )
            .as_raw_html()
        )

    # Download the data
    @render.download(filename="income.csv")
    def download_data():
        # Yield a function that writes to the file path Shiny provides
        yield data().to_csv(index=False)
