"""
Main application module
"""

import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import polars as pl
from shiny import App
from shiny import reactive
from shiny import render
from shiny import run_app
from shiny import ui
from shiny.types import ImgData

import lemonade_stand
from lemonade_stand.config import UserConfig
from lemonade_stand.data import UserData
from lemonade_stand.data import get_data
from lemonade_stand.shiny import auth_server
from lemonade_stand.shiny import expense_server
from lemonade_stand.shiny import expense_ui
from lemonade_stand.shiny import home_server
from lemonade_stand.shiny import home_ui
from lemonade_stand.shiny import income_server
from lemonade_stand.shiny import income_ui
from lemonade_stand.shiny import savings_server
from lemonade_stand.shiny import savings_ui
from lemonade_stand.shiny import settings_server
from lemonade_stand.shiny import settings_ui
from lemonade_stand.shiny import user_guide_server
from lemonade_stand.shiny import user_guide_ui
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
ASSETS_DIR = Path(lemonade_stand.__file__).parent / "shiny" / "assets"


# Define the application UI and Server using Shiny
app_ui = ui.page_navbar(
    # Inject the custom configuration files
    ui.head_content(
        ui.include_css(ASSETS_DIR / "css" / "global.css"),
        ui.include_css(ASSETS_DIR / "css" / "login.css"),
        ui.include_css(ASSETS_DIR / "css" / "settings.css"),
    ),
    ui.nav_spacer(),
    # Main content page
    home_ui("Home"),
    income_ui("Income"),
    savings_ui("Savings"),
    expense_ui("Expense"),
    # Allow dark mode
    ui.nav_spacer(),
    ui.nav_control(ui.input_dark_mode(id="view_mode")),
    # Add Side bar
    sidebar=ui.sidebar(
        user_guide_ui("user_guide"),
        settings_ui("user_settings"),
        title="Options",
        style="font-weight: bold;",
    ),
    title=ui.div(
        ui.output_image("logo_svg", inline=True),
        ui.h5(
            "Lemonade Stand",
            style="font-style: italic; letter-spacing: 0.02rem; margin-bottom: 0;",
        ),
        style="display: flex; justify-content: flex-start; align-items: flex-end; width: 100%; max-width: 28%;",
    ),
    lang="en",
    id="pages",
)


def server(input, output, session):  # noqa: ARG001
    """
    The main application server
    """

    # Create argparse object instance
    parser = argparse.ArgumentParser(description="Lemonade Stand application")
    parser.add_argument(
        "--as", type=str, dest="as_", default="user", help="The run option (optional)."
    )

    # Save parsed arguments
    args = parser.parse_args()

    # Check whether to initialize login page
    if args.as_ == "dev":
        LOGGER.info("Initializing application in developer mode")

        # Set up a reactive run config
        build_params = UserConfig(dev_mode=True)
        data_path: reactive.Value[Path] = reactive.Value(build_params.statement_dir)

    else:
        LOGGER.info("Initializing application in user mode")

        # Set up a reactive run config
        build_params = auth_server("user_login")
        data_path: reactive.Value[Path] = reactive.Value(build_params.statement_dir)

    # Initialize application documentation and settings
    @reactive.Effect
    def _():
        user_guide_server("user_guide")
        build_params = settings_server("user_settings")()
        data_path.set(build_params.statement_dir)

    LOGGER.info("Using configuration: \n%s", str(build_params))

    # Reactively set up the user data
    @reactive.Calc
    @reactive.event(data_path)
    def dataset() -> UserData | SimpleNamespace:
        with ThreadPoolExecutor() as executor:
            # Submit the task
            future = executor.submit(get_data, run_config=build_params)

            with ui.Progress(min=0, max=1) as p:
                counter = 0

                while not future.done():
                    counter += 1
                    p.set(message=f"Processing data... ({counter}s)")
                    time.sleep(1)

            # Retrieve the resulting user-data and save it in the reactive value
            return future.result()

    # Build tab pages
    @reactive.effect
    @reactive.event(data_path, dataset)
    def _():
        user_data = dataset()

        # Stack all the datasets for the home-page
        stacked_df = pl.union(
            [
                user_data.income,
                user_data.savings,
                user_data.expenses,
                user_data.unknown,
            ],
            how="diagonal",
        )

        if stacked_df.shape[0] > 0:
            # Call the page servers
            home_server("Home", input.view_mode, stacked_df)
            income_server("Income", input.view_mode, user_data.income)
            savings_server("Savings", input.view_mode, user_data.savings)
            expense_server("Expense", input.view_mode, user_data.expenses)
        else:
            # Read in markdown contents
            no_data_md = ASSETS_DIR / "markdown" / "no_data.md"

            with no_data_md.open("r", encoding="utf-8") as file:
                no_data_text = file.read()

            # Display modal with message
            ui.modal_show(
                ui.modal(
                    ui.markdown(no_data_text),
                    size="l",
                    easy_close=True,
                    footer=ui.modal_button("Close"),
                    style="padding-left: 5rem;",
                )
            )

    @render.image
    def logo_svg():
        img: ImgData = {
            "src": str(ASSETS_DIR / "images" / "app_logo.svg"),
            "width": "100%",
            "height": "100%",
        }
        return img


def initialize_app() -> None:
    """
    Temporary function to initialize the shiny application
    """

    run_app(
        app="lemonade_stand.app:app",
        reload=True,
    )


# Connect everything
app = App(app_ui, server)
