"""
Main application module
"""

from pathlib import Path

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


# Define the application UI and Server using Shiny
app_ui = ui.page_navbar(
    # Main content page
    home_ui("Home"),
    income_ui("Income"),
    savings_ui("Savings"),
    expense_ui("Expense"),
    # Allow dark mode
    ui.nav_spacer(),
    ui.nav_control(ui.input_dark_mode(id="view_mode")),
    # Add Side bar
    sidebar=ui.sidebar(settings_ui("my_settings"), title="User Options"),
    title="Lemonade Stand",
    id="pages",
)


def server(input, output, session):  # noqa: ARG001
    """
    The main application server
    """

    # Pull the user data
    user_data = get_data()

    # Catch the returned reactive values
    user_prefs = settings_server("my_settings")  # noqa: F841

    home_server("Home", user_data)
    income_server("Income", user_data)
    savings_server("Savings", user_data)
    expense_server("Expense", user_data)


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
