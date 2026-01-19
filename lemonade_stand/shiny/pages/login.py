"""
User settings page layout configurations
"""

from pathlib import Path

from faicons import icon_svg
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shiny.types import ImgData

import lemonade_stand
from lemonade_stand.config import UserConfig
from lemonade_stand.shiny.shared import LoginCredentials
from lemonade_stand.shiny.shared import add_user_credentials
from lemonade_stand.shiny.shared import validate_user_credentials
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
RUN_CONFIG = UserConfig()
APP_LOGO = (
    Path(lemonade_stand.__file__).parent
    / "shiny"
    / "assets"
    / "images"
    / "app_logo.svg"
)


@module.server
def auth_server(input, output, session):  # noqa: ARG001
    """
    A server module for the settings page
    """

    # Define reactive containers to track execution and hold the information
    valid_statement_path = reactive.Value(False)
    login_initialized = reactive.Value(False)
    auth_feedback = reactive.Value()

    @render.image
    def logo_svg():
        img: ImgData = {
            "src": str(APP_LOGO),
            "width": "100%",
            "height": "100%",
        }
        return img

    ## **** LOGIN MODAL ****
    def show_login_modal():
        """
        A function that sets up the log-in modal ui
        """

        LOGGER.info("Building Log-in page...")

        # Set up the modal
        login_modal = ui.modal(
            ui.div(
                ui.span(
                    ui.output_image("logo_svg", inline=True),
                    style="width: 35%; display: block; margin: 10% auto 10% auto;",
                ),
                ui.h5(
                    "Sign in with your Account",
                    style="margin-bottom: 1.8rem",
                    class_="items-centered",
                ),
                ui.div(
                    ui.input_text_area(
                        id="user_name",
                        label=None,
                        placeholder="Username",
                        autocomplete="username",
                        autoresize=True,
                    ),
                    ui.output_ui(id="confirm_valid_username"),
                    class_="items-centered",
                ),
                ui.div(
                    ui.input_password(
                        id="user_password",
                        label=None,
                        placeholder="Password",
                    ),
                    ui.output_ui(id="confirm_valid_password"),
                    class_="items-centered",
                ),
                ui.output_ui(id="note_user_credentials"),
            ),
            ui.div(
                ui.input_action_button(
                    id="confirm_login", label="Login", style="margin: auto;"
                ),
                style="margin: 0.5rem auto 2rem auto; width: 100%; display: flex; justify-content: center;",
            ),
            ui.div(
                ui.p("New here? "),
                ui.input_action_link(
                    "open_signup", "Create an account", class_="general-link"
                ),
                style="display: flex; justify-content: center; gap: 4px; font-size: .9375rem",
            ),
            ui.div(
                ui.input_checkbox(
                    id="skip_login", label="always skip login", value=False
                ),
                style="display: flex; justify-content: flex-start; margin-top: 1rem;",
                class_="checkbox-note",
            ),
            size="m",
            footer=None,
            easy_close=False,
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(login_modal)

    ## **** SIGN UP MODAL ****
    def show_signup_modal():
        """
        A function that sets up the sign-up modal ui
        """

        LOGGER.info("Initializing Sign-up page...")

        # Set up the modal
        signup_modal = ui.modal(
            ui.div(
                ui.span(
                    ui.output_image("logo_svg", inline=True),
                    style="width: 10%; max-width: 18%;",
                ),
                ui.h5("Lemonade-Stand", style="font-style: italic; margin: 0;"),
                style="display: flex; justify-content: center; align-items: flex-end; width: 100%;",
            ),
            ui.h5(
                "Create your Account",
                style="font-weight: bold; margin-top: 10%; margin-bottom: 5%;",
            ),
            ui.input_text(
                id="signup_user_name",
                placeholder="Username *",
                label=None,
            ),
            ui.input_text(
                id="signup_user_password",
                placeholder="Password *",
                label=None,
            ),
            ui.span(
                "Personal information ",
                ui.em("(Optional)", style="font-style: italic; opacity: 0.8;"),
                style="margin-top: 5%; margin-bottom: 2%;",
            ),
            ui.input_text(
                id="signup_first_name",
                placeholder="First Name",
                label=None,
            ),
            ui.input_text(
                id="signup_last_name",
                placeholder="Last Name",
                label=None,
            ),
            ui.input_selectize(
                id="signup_gender",
                label=None,
                choices=["", "Female", "Male", "Non-binary", "Other"],
                selected=None,
                options={
                    "placeholder": "Gender",
                    "allowEmptyOption": True,
                },
            ),
            ui.div(
                ui.input_text(
                    id="statement_path",
                    label="Statements directory path:",
                    placeholder="A folder that contains your statement pdfs",
                    width="75%",
                ),
                ui.output_ui(id="confirm_valid_path"),
                style="margin-top: 5%",
            ),
            ui.div(
                ui.input_action_button(
                    id="confirm_signup", label="Create Account", style="margin: auto;"
                ),
                style="margin-top: 20px; width: 100%; display: flex; justify-content: center;",
            ),
            size="m",
            easy_close=False,
            footer=ui.div(
                ui.p("Already have an account?"),
                ui.input_action_link("open_login", "Sign in", class_="general-link"),
                style="display: flex; justify-content: flex-end; align-items: flex-start; gap: 4px;",
            ),
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(signup_modal)

    ## **** USER CREDENTIAL VALIDATIONS ****
    def process_login() -> LoginCredentials:
        """
        Validates the user's credentials on log in
        """

        # Validate the user credentials
        check_result = validate_user_credentials(
            username=input.user_name(),
            userpassword=str(input.user_password()).encode("utf-8"),
        )

        LOGGER.info(
            "Validated user credentials. Boolean results: \n%s", str(check_result)
        )

        return check_result

    ## **** USER CREDENTIAL ADDITIONS ****
    def process_signup() -> LoginCredentials:
        """
        Processes the user's credentials on signup
        """

        # Save the user information
        add_result = add_user_credentials(
            username=input.signup_user_name(),
            userpassword=(input.signup_user_password()).encode("utf-8"),
            first_name=input.signup_first_name(),
            last_name=input.signup_last_name(),
            gender=input.signup_gender(),
        )

        LOGGER.info("Added user credentials. Boolean results: \n%s", str(add_result))

        return add_result

    # Reactively show the modals
    @reactive.effect
    def _():
        if (not login_initialized()) and (not RUN_CONFIG.always_skip_login):
            show_login_modal()
            login_initialized.set(True)

    @reactive.effect
    @reactive.event(input.open_login)
    def _():
        LOGGER.info("User clicked open log-in button...")
        show_login_modal()

    @reactive.effect
    @reactive.event(input.open_signup)
    def _():
        LOGGER.info("User clicked open sign-up button...")
        show_signup_modal()

    # Display errors for the user
    @render.ui
    def note_user_credentials():
        auth_result = auth_feedback()

        if auth_result is None:
            return None
        elif auth_result and len(auth_result.invalid_credentials) > 0:
            LOGGER.info(
                "Invalid credentials '%s'. Displaying user notification...",
                str(auth_result.invalid_credentials),
            )

            return ui.div(
                f"Invalid {' and '.join(auth_result.invalid_credentials)}!",
                class_="invalid-note",
            )

    @render.ui
    def confirm_valid_username():
        # Show note on login click
        auth_result = auth_feedback()
        if auth_result and auth_result.username:
            return icon_svg("circle-check", fill="green")
        else:
            return None

    @render.ui
    def confirm_valid_password():
        # Show note on login click
        auth_result = auth_feedback()
        if auth_result and auth_result.password:
            return icon_svg("circle-check", fill="green")
        else:
            return None

    @render.ui
    def confirm_valid_path():
        user_statements_dir = Path(input.statement_path())

        # Start displays only when user has an input
        if input.statement_path() == "":
            return None

        # Validate that the path exists
        elif user_statements_dir.exists():
            pdf_files = list(user_statements_dir.glob("*.pdf"))

            # Update statement directory containers if dir has files
            if len(pdf_files) > 0:
                valid_statement_path.set(True)
                RUN_CONFIG.update_attribute(
                    mappings={"statement_dir": user_statements_dir}
                )

                return None
            else:
                return ui.div(
                    "Statement folder does not contain any statement files. Please confirm that '.pdf' files exist",
                    class_="invalid-note",
                )
        else:
            return ui.div(
                "Invalid statement path! Path does not exist",
                class_="invalid-note",
            )

    @reactive.effect
    @reactive.event(input.confirm_login)
    def handle_login():
        login_result = process_login()
        auth_feedback.set(login_result)

        if login_result.username and login_result.password:
            LOGGER.info("Login successful!")

            # Update statement directory
            RUN_CONFIG.update_attribute(
                mappings={"always_skip_login": input.skip_login()}
            )

            ui.modal_remove()
        else:
            pass

    @reactive.effect
    @reactive.event(input.confirm_signup)
    def handle_signup():
        signup_result = process_signup()
        auth_feedback.set(signup_result)

        # Move forward if a valid statement path was given
        if valid_statement_path():
            if signup_result.username and signup_result.password:
                LOGGER.info("Signup successful.")

                ui.modal_remove()
            else:
                pass

    # Process the statements
    return RUN_CONFIG
