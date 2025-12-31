"""
Savings page layout configurations
"""

from pathlib import Path

from shiny import module
from shiny import ui

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def savings_ui():
    """
    A UI module for the savings page
    """

    return ui.nav_panel(
        "Savings",
    )


@module.server
def savings_server(input, output, session, view_mode_setting, data_df):  # noqa: ARG001
    """
    A server module for the savings page
    """

    pass
