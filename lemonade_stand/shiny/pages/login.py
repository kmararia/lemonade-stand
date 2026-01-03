"""
User settings page layout configurations
"""

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from faicons import icon_svg
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shiny.types import ImgData

import lemonade_stand
from lemonade_stand.config import UserConfig
from lemonade_stand.data import get_data
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils.credentials import LoginCredentials
from lemonade_stand.utils.credentials import add_user_credentials
from lemonade_stand.utils.credentials import validate_user_credentials

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
    login_initialized = reactive.Value(False)
    transaction_data = reactive.Value()
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

        LOGGER.info("Initializing Log-in page...")

        # Set up the modal
        login_modal = ui.modal(
            ui.div(
                ui.span(
                    ui.output_image("logo_svg", inline=True),
                    style="width: 35%; display: block; margin: 10% auto 10% auto;",
                ),
                ui.h5(
                    "Sign in with your Account",
                    style="font-weight: bold; margin-bottom: 5%",
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
            footer=ui.div(
                ui.p("No account? "),
                ui.input_action_link("open_signup", "Sign up", class_="general-link"),
                style="display: flex; justify-content: flex-end; align-items: flex-start; gap: 4px; font-size: .9375rem",
            ),
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
        settings_modal = ui.modal(
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
        ui.modal_show(settings_modal)

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

    ## **** CLEAR ACTIVE MODALS ****
    def unlock_app(user_run_config: UserConfig):
        """ """

        # Initialize a thread-pool executor
        with ThreadPoolExecutor() as executor:
            # Submit the task
            future = executor.submit(get_data, run_config=user_run_config)

            with ui.Progress(min=0, max=1) as p:
                counter = 0

                # Update UI as long as the thread is still alive
                while not future.done():
                    counter += 1
                    p.set(value=None, message=f"Processing... ({counter}s)")
                    time.sleep(1)

            # Retrieve the resulting user-data and save it in the reactive value
            transaction_data.set(future.result())

        ui.modal_remove()

    # Reactively show the modals
    @reactive.effect
    def _():
        if not login_initialized():
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
                class_="login-invalid-note",
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

    @reactive.effect
    @reactive.event(input.confirm_login)
    def handle_login():
        login_result = process_login()
        auth_feedback.set(login_result)

        if login_result.username and login_result.password:
            LOGGER.info("Login successful!")

            unlock_app(user_run_config=RUN_CONFIG)
        else:
            pass

    @reactive.effect
    @reactive.event(input.confirm_signup)
    def handle_signup():
        signup_result = process_signup()
        auth_feedback.set(signup_result)

        # Validate that the path exists
        user_statements_dir = Path(input.statement_path())
        if not user_statements_dir.exists():
            raise Exception

        if signup_result.username and signup_result.password:
            LOGGER.info("Signup successful.")

            # Update statement directory
            RUN_CONFIG.update_attribute(mappings={"statement_dir": user_statements_dir})

            unlock_app(user_run_config=RUN_CONFIG)
        else:
            pass

    # Process the statements
    return transaction_data
