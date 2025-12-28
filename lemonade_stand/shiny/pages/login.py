"""
User settings page layout configurations
"""

import time
from pathlib import Path

from faicons import icon_svg
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui

import lemonade_stand
from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import validate_user_credentials

LOGGER = set_up_logger(Path(__file__).stem)
CSS_FILE = (
    Path(lemonade_stand.__file__).parent / "shiny" / "assets" / "css" / "login.css"
)
APP_DIR = AppDir()


@module.ui
def login_ui():
    """
    A UI module for the settings page
    """

    return None


@module.server
def login_server(input, output, session):  # noqa: ARG001
    """
    A server module for the settings page
    """

    @reactive.effect
    def _():
        # Set up the modal
        login_modal = ui.modal(
            ui.div(
                ui.div(
                    ui.input_text_area(
                        id="user_name",
                        label=None,
                        placeholder="Username",
                        autocomplete="username",
                        autoresize=True,
                    ),
                    ui.output_ui(id="confirm_valid_username"),
                    class_="login-modal-input",
                ),
                ui.div(
                    ui.input_password(
                        id="user_password",
                        label=None,
                        placeholder="Password",
                    ),
                    ui.output_ui(id="confirm_valid_password"),
                    class_="login-modal-input",
                ),
                ui.output_ui(id="note_user_credentials"),
                class_="login-modal-content",
            ),
            ui.div(
                ui.input_action_button(
                    id="confirm_login", label="Login", style="margin: auto;"
                ),
                style="margin-top: 20px; width: 100%; display: flex; justify-content: center;",
            ),
            size="m",
            footer=None,
            easy_close=False,
            title="Login or Sign up",
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(login_modal)

    @reactive.Calc
    @reactive.event(input.confirm_login)
    def credential_check():
        # Validate the user credentials
        return validate_user_credentials(
            username=input.user_name(), userpassword=input.user_password()
        )

    @render.ui
    def note_user_credentials():
        # Show note on login completion
        invalid_creds = credential_check().invalid_credentials
        if not len(invalid_creds) > 0:
            return ui.div(
                f"Invalid {' and '.join(invalid_creds)}!",
                class_="login-invalid-note",
            )

    @render.ui
    def confirm_valid_username():
        # Show note on login completion
        if credential_check().username:
            return icon_svg("circle-check", fill="green")
        else:
            return None

    @render.ui
    def confirm_valid_password():
        # Show note on login completion
        if credential_check().password:
            return icon_svg("circle-check", fill="green")
        else:
            return None

    @reactive.effect
    async def _():
        # Show note on login completion
        if (credential_check().username) and (credential_check().password):
            with ui.Progress(min=1, max=10) as p:
                p.set(
                    message="Checking login credentials...",
                    detail="This may take a while...",
                )

                for i in range(0, 10):
                    p.set(i, message="Computing")
                    time.sleep(0.1)

            ui.modal_remove()
        else:
            pass
