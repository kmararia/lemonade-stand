"""
Main application module
"""

import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import polars as pl
from faicons import icon_svg
from shiny import App
from shiny import reactive
from shiny import run_app
from shiny import ui

import lemonade_stand
from lemonade_stand.config import UserConfig
from lemonade_stand.data import UserData
from lemonade_stand.data import get_data
from lemonade_stand.shiny import auth_server
from lemonade_stand.shiny import exclude_server
from lemonade_stand.shiny import exclude_ui
from lemonade_stand.shiny import expense_server
from lemonade_stand.shiny import expense_ui
from lemonade_stand.shiny import home_server
from lemonade_stand.shiny import home_ui
from lemonade_stand.shiny import income_server
from lemonade_stand.shiny import income_ui
from lemonade_stand.shiny import mappings_category_server
from lemonade_stand.shiny import mappings_category_ui
from lemonade_stand.shiny import mappings_type_server
from lemonade_stand.shiny import mappings_type_ui
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
        ui.tags.link(rel="stylesheet", type="text/css", href="css/global.css"),
    ),
    ui.nav_spacer(),
    # Main content page
    home_ui("Home"),
    income_ui("Income"),
    savings_ui("Savings"),
    expense_ui("Expense"),
    # Allow dark mode
    ui.nav_spacer(),
    ui.nav_control(
        ui.span(
            ui.input_task_button(
                id="refresh_data",
                label="",
                label_busy="",
                icon=icon_svg("rotate-right"),
                icon_busy=icon_svg("spinner"),
                type="default",
                class_="task-button",
            ),
            ui.input_dark_mode(id="view_mode"),
            style="display: flex; justify-content: flex-end; gap: 0.5rem;",
        )
    ),
    # Add Side bar
    sidebar=ui.sidebar(
        user_guide_ui("user_guide"),
        settings_ui("user_settings"),
        exclude_ui("mappings_exclude"),
        ui.accordion(
            ui.accordion_panel(
                ui.span("Mappings", class_="sidebar-link"),
                mappings_type_ui("mappings_type"),
                mappings_category_ui("mappings_category"),
                value="mappings_panel",
                icon=icon_svg("code"),
            ),
            id="mapping_accordion",
            open=False,
        ),
        ui.input_switch(
            id="show_excluded",
            label=ui.p("Show excluded", class_="sidebar-link"),
            value=False,
        ),
        title=ui.h5("Options"),
    ),
    title=ui.div(
        ui.img(src="images/app_logo.svg", class_="logo-image"),
        ui.span("Lemonade Stand", class_="brand-name"),
        class_="items-bottom-left",
    ),
    lang="en",
    id="pages",
)


def server(input, output, session):  # noqa: ARG001
    """
    The main application server
    """

    # Define reactive values to track execution
    data_refresh_tracker: reactive.Value[int] = reactive.Value(0)
    build_params: reactive.Value[UserConfig] = reactive.Value()
    data_path: reactive.Value[Path] = reactive.Value()

    # Create argparse object instance
    parser = argparse.ArgumentParser(description="Lemonade Stand application")
    parser.add_argument(
        "--as", type=str, dest="as_", default="user", help="The run option (optional)."
    )

    # Save parsed arguments
    args = parser.parse_args()

    LOGGER.info("Initializing application in '%s' mode", str(args.as_))

    # Check whether to initialize login page
    run_config = (
        UserConfig(dev_mode=True) if args.as_ == "dev" else auth_server("user_login")
    )

    # Build app documentation and settings page
    user_guide_server("user_guide")
    mappings_type_server("mappings_type")
    mappings_category_server("mappings_category")
    exclude_server("mappings_exclude")
    settings_config = settings_server("user_settings")

    # Update the reactive values
    build_params.set(run_config)
    data_path.set(run_config.statement_dir)

    # Update build configurations on settings close
    @reactive.Effect
    @reactive.event(settings_config.trigger)
    def _():
        # Log out if the user purged the application
        if settings_config.log_out:
            LOGGER.info("Initializing login after purge...")

            login_config = auth_server("user_purge_login")
            build_params.set(login_config)
            data_path.set(login_config.statement_dir)
        else:
            new_settings = settings_config.user_config
            build_params.set(new_settings)

            if new_settings.statement_dir != data_path():
                data_path.set(new_settings.statement_dir)

        LOGGER.info("Using configuration: \n%s", str(build_params()))

    # Reactively set up the user data
    @reactive.Calc
    @reactive.event(input.refresh_data, data_path)
    def dataset() -> UserData | SimpleNamespace:
        current_config = build_params()

        with ThreadPoolExecutor() as executor:
            # Determine appropriate function to use
            if data_refresh_tracker.get() < input.refresh_data():
                LOGGER.info("Refreshing the data on user request...")
                prep_data_func = UserData
            else:
                LOGGER.info("Pulling the data for shiny app...")
                prep_data_func = get_data

            # Submit the task
            future = executor.submit(prep_data_func, config=current_config)

            with ui.Progress(min=0, max=1) as p:
                counter = 0

                while not future.done():
                    counter += 1
                    p.set(message=f"Processing your data... ({counter}s)")
                    time.sleep(1)

            # Retrieve the resulting user-data and save it in the reactive value
            return future.result()

    # Build tab pages
    @reactive.effect
    def _():
        user_data = dataset()

        # Stack all the datasets for the home-page
        stack_df_list = [
            user_data.income,
            user_data.savings,
            user_data.expenses,
            user_data.unknown,
        ]
        stacked_df = pl.union(
            [
                x
                if input.show_excluded()
                else x.filter(
                    ~pl.coalesce("exclude_flag", pl.lit(False))
                )  # Adding redundancy check incase exclude flag was not populated
                for x in stack_df_list
            ],
            how="diagonal",
        ).select(
            pl.exclude("extract_date")
            if input.show_excluded()
            else pl.exclude("extract_date", "exclude_flag")
        )

        # Call the page servers
        if stacked_df.shape[0] > 0:
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


def initialize_app() -> None:
    """
    Temporary function to initialize the shiny application
    """

    run_app(
        app="lemonade_stand.app:app",
        reload=True,
    )


# Connect everything
app = App(app_ui, server, static_assets=ASSETS_DIR)
