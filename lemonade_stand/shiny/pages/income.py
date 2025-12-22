"""
Income page layout configurations
"""

from pathlib import Path

from shiny import module
from shiny import ui

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def income_ui():
    """
    A UI module for the income page
    """

    return ui.nav_panel(
        "Income",
    )


@module.server
def income_server(input, output, session, data_df):  # noqa: ARG001
    """
    A server module for the income page
    """

    pass
