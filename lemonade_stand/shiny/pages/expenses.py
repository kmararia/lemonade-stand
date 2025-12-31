"""
Expenses page layout configurations
"""

from pathlib import Path

from shiny import module
from shiny import ui

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def expense_ui():
    """
    A UI module for the expense page
    """

    return ui.nav_panel(
        "Expense",
    )


@module.server
def expense_server(input, output, session, view_mode_setting, data_df):  # noqa: ARG001
    """
    A server module for the expense page
    """

    pass
