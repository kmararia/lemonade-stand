"""
Main application module
"""

from pathlib import Path

import polars as pl
from shiny import App
from shiny import run_app
from shiny import ui

from lemonade_stand.data import get_data
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
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
CSS_DIR = Path(__file__).parent / "shiny" / "assets" / "css"

# Define the application UI and Server using Shiny
app_ui = ui.page_navbar(
    # Inject the custom configuration files
    ui.head_content(
        ui.include_css(CSS_DIR / "global.css"),
        ui.include_css(CSS_DIR / "settings.css"),
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
        settings_ui("my_settings"), title="User Options", style="font-weight: bold;"
    ),
    title="Lemonade Stand",
    id="pages",
)


def server(input, output, session):  # noqa: ARG001
    """
    The main application server
    """

    # Catch the returned reactive values
    user_prefs = settings_server("my_settings")  # noqa: F841

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
