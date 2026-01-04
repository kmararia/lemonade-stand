""" """

from collections.abc import Callable
from pathlib import Path

import polars as pl

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


def build_chart(
    func_plotly: Callable,
    data_df: pl.DataFrame,
    x_var: str,
    y_var: str,
    color_var: str,
    view_mode: str,
):
    """
    A function to build a plotly bar graph
    """

    LOGGER.info("Building page graph...")

    # Set theme-specific colors
    if view_mode == "light":
        theme = "plotly_white"
        font_color = "black"
        hover_bg_color = "white"

    else:
        theme = "plotly_dark"
        font_color = "white"
        hover_bg_color = "#333"

    # Create the figure
    fig = func_plotly(
        data_frame=data_df,
        x=x_var,
        y=y_var,
        color=color_var,
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
    fig.update_traces(hovertemplate="<b>%{fullData.name}</b>: $%{y:.2f}<extra></extra>")

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
