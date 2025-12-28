"""
Main application module
"""

from pathlib import Path

import polars as pl
from shiny import App
from shiny import render
from shiny import run_app
from shiny import ui
from shiny.types import ImgData

import lemonade_stand
from lemonade_stand.data import get_data
from lemonade_stand.shiny import expense_server
from lemonade_stand.shiny import expense_ui
from lemonade_stand.shiny import home_server
from lemonade_stand.shiny import home_ui
from lemonade_stand.shiny import income_server
from lemonade_stand.shiny import income_ui
from lemonade_stand.shiny import login_server
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

    # Initialize login page
    login_server("user_login")

    # Catch the returned reactive values
    user_prefs = settings_server("user_settings")  # noqa: F841

    # Initialize application documentation
    user_guide_server("user_guide")

    # Pull the user data
    user_data = get_data()

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

    # Call the page servers
    home_server("Home", input.view_mode, stacked_df)
    income_server("Income", user_data.income)
    savings_server("Savings", user_data.savings)
    expense_server("Expense", user_data.expenses)

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
