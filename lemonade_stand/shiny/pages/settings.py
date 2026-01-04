"""
User settings page layout configurations
"""

import shutil
from pathlib import Path

from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui

from lemonade_stand.config import AppDir
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_DIR = AppDir()


@module.ui
def settings_ui():
    """
    A UI module for the settings page
    """

    return ui.input_action_link("open_settings", "⚙️ Settings", class_="sidebar-link")


@module.server
def settings_server(input, output, session):  # noqa: ARG001
    """
    A server module for the settings page
    """

    # Create reactive values to track events
    reactive_config = reactive.Value(UserConfig())
    is_purged = reactive.Value(False)

    @reactive.effect
    @reactive.event(input.open_settings)
    def _():
        # Set up the modal
        settings_modal = ui.modal(
            ui.h5("Transaction statements"),
            ui.br(),
            ui.input_text(
                id="statement_path",
                label="Statements directory path:",
                placeholder=str(reactive_config().statement_dir),
                autocomplete="on",
                width="80%",
            ),
            ui.div(
                ui.input_switch(
                    id="always_refresh_data",
                    label="Always refresh full data",
                    value=reactive_config().always_refresh_data,
                    width="15rem",
                ),
                ui.span(
                    ui.output_ui(id="note_data_refresh"), style="margin-bottom: 1.2rem;"
                ),
                style="display: flex; align-items: center; gap: 1rem; margin-top: 2rem;",
            ),
            ui.input_switch(
                id="always_skip_login",
                label="Always skip login",
                value=reactive_config().always_skip_login,
            ),
            ui.br(),
            # User experience settings
            ui.h5("User experience"),
            ui.input_switch("show_decimals", "Show decimal places", True),
            ui.br(),
            # Purging danger zone!
            ui.div(
                ui.h6("Danger Zone!!"),
                ui.input_switch(id="purge_app", label="Purge all data", value=False),
                ui.output_ui(id="confirm_purge"),
            ),
            size="l",
            easy_close=True,
            footer=ui.modal_button("Dismiss"),
            title="Main Application Settings",
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(settings_modal)

    # Reactively update the ui and config object
    @reactive.effect
    @reactive.event(
        input.statement_path, input.always_refresh_data, input.always_skip_login
    )
    def _():
        reactive_config().update_attribute(
            mappings={
                "statement_dir": str(input.statement_path()),
                "always_refresh_data": input.always_refresh_data(),
                "always_skip_login": input.always_skip_login(),
            }
        )

        LOGGER.info("Settings configuration: \n%s", str(reactive_config()))

    # Display full data refresh disclaimer
    @render.ui
    def note_data_refresh():
        # Only show if the switch is True
        if input.always_refresh_data():
            return ui.span(
                "Note: A full data refresh might slow down your application depending on your data size.",
                class_="switch-note",
            )
        return None

    # Display and request confirmation to purge application
    @render.ui
    def confirm_purge():
        if is_purged():
            return ui.input_text(
                id="purge_confirmation",
                label=ui.span(
                    "Application purged! All saved data has been removed",
                    class_="login-invalid-note",
                ),
                width="50%",
            )

        if input.purge_app():
            return ui.div(
                ui.input_text(
                    id="user_type_purge",
                    label=ui.span(
                        "Type 'purge' to confirm action:  This action cannot be undone",
                        class_="switch-note",
                    ),
                    width="50%",
                ),
                ui.input_action_button(
                    id="user_confirm_purge",
                    label="confirm",
                    style="height: 2.2rem; width: 5rem; margin: auto 0 1rem 0; display: inline-flex; justify-content: center; align-items: center;",
                ),
                style="display: flex; justify-content: flex-start; align-items: flex-end; gap: 20px;",
            )
        return None

    # Purge application if user confirmed
    @reactive.effect
    @reactive.event(input.user_confirm_purge)
    def _():
        if (input.purge_app()) and (input.user_type_purge().lower() == "purge"):
            LOGGER.info(
                "User confirmed application purge: '%s'", input.user_type_purge()
            )

            # Confirm that the directory is indeed the application dir
            remove_path = APP_DIR.root_dir
            if remove_path.name == "lemonade-stand":
                shutil.rmtree(remove_path)

                # Ouput log info and update the reactive state
                LOGGER.info("Application directory cleared! \n\t'%s'", str(remove_path))
                is_purged.set(True)

    # Return a reactive user configuration object
    return reactive_config
