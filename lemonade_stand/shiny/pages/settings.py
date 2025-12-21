"""
User settings page layout configurations
"""

from pathlib import Path
from types import SimpleNamespace

from shiny import module
from shiny import reactive
from shiny import ui

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def settings_ui():
    """
    A UI module for the settings page
    """

    return ui.input_action_link("open_settings", "⚙️ Settings", class_="nav-link")


@module.server
def settings_server(input, output, session):  # noqa: ARG001
    """
    A server module for the settings page
    """

    @reactive.effect
    @reactive.event(input.open_settings)
    def _():
        # Set up the modal
        settings_modal = ui.modal(
            ui.h5("Transaction statements"),
            ui.input_text(
                "statement_path",
                "Statements directory path:",
                placeholder=str(AppDir.current_dir),
            ),
            ui.input_switch("show_data", "Don't ask for path again", value=True),
            ui.br(),
            ui.h5("User experience"),
            ui.input_select(
                "theme_accent", "Accent Color", ["Blue", "Green", "Orange"]
            ),
            ui.input_switch("show_decimals", "Show decimal places", True),
            title="Main Application Settings",
            footer=ui.modal_button("Dismiss"),
            easy_close=True,
            size="l",
        )

        # Unhide the modal
        ui.modal_show(settings_modal)

    # Return the inputs as a dictionary of reactive values
    return SimpleNamespace(
        accent=lambda: input.theme_accent(),
        decimals=lambda: input.show_decimals(),
    )
