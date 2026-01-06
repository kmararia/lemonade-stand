"""
A user mapping configurations for the category
"""

import json
from pathlib import Path

from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
CONFIG_PATH = AppDir().category_config_path


@module.ui
def mappings_ui():
    """
    A UI module for the user-guide page
    """

    return ui.input_action_link(
        "open_mappings", "{ } User Mappings", class_="sidebar-link"
    )


@module.server
def mappings_server(input, output, session):  # noqa: ARG001
    """
    A server module for the user-guide page
    """

    # Read in the category config file if it exists
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r") as file:
            category_mappings: reactive.Value[dict] = reactive.Value(json.load(file))
    else:
        category_mappings: reactive.Value[dict] = reactive.Value({})

    @reactive.effect
    @reactive.event(input.open_mappings)
    def _():
        # Set up the modal
        mappings_modal = ui.modal(
            ui.input_file(
                id="input_json",
                label="File upload mappings",
                accept=[".json", ".csv"],
                multiple=False,
            ),
            ui.p("Manual input mappings"),
            ui.div(
                ui.span(
                    ui.input_text(
                        id="key_mapping", label=None, placeholder="Key substring"
                    ),
                    ui.input_text(
                        id="value_mapping", label=None, placeholder="Category to map to"
                    ),
                    style="display: flex; justify-content: flex-start; gap: 0.5rem;",
                ),
                ui.input_action_button(
                    id="add_mapping",
                    label="Add",
                    style="display: flex; justify-content: center; align-items: center; max-height: 2.3rem; margin-left: 0.5rem;",
                ),
                style="display: flex; justify-content: space-between; margin-bottom: 1rem;",
            ),
            ui.output_ui(id="confirm_override"),
            ui.output_text_verbatim(id="display_json", placeholder=False),
            ui.div(
                ui.download_button(
                    "download_json", "Download json", class_="download-button"
                ),
                style="display: flex; justify-content: flex-end; align-items: center;",
            ),
            size="l",
            easy_close=True,
            footer=ui.modal_button("Close"),
            title="USER MAPPINGS",
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(mappings_modal)

    @render.ui
    @reactive.event(input.add_mapping)
    def confirm_override():
        key_value = input.key_mapping()

        if key_value in category_mappings():
            return ui.div(
                ui.p(
                    f"Key '{key_value}' already exists. Would you like to override the current key-value mapping? ",
                    class_="login-invalid-note",
                ),
                ui.input_action_button(
                    id="confirm_add_mapping",
                    label="Yes",
                    style="display: flex; justify-content: center; align-items: center; max-height: 2.3rem; margin-left: 0.5rem;",
                ),
                style="display: flex; justify-content: space-between; margin-bottom: 1rem;",
            )
        else:
            return ui.div()

    @reactive.effect
    @reactive.event(input.add_mapping)
    def _():
        key_input = input.key_mapping()
        value_input = input.value_mapping()

        # If it's a new key, update immediately
        if key_input not in category_mappings():
            new_data = {**category_mappings(), key_input: value_input}
            category_mappings.set(new_data)

            # Save to file
            with CONFIG_PATH.open("w") as file:
                json.dump(new_data, file, indent=4)

    @reactive.effect
    @reactive.event(input.confirm_add_mapping)
    def _():
        # Update after user confirms
        new_data = {**category_mappings(), input.key_mapping(): input.value_mapping()}
        category_mappings.set(new_data)

        # Save to file
        with CONFIG_PATH.open("w") as file:
            json.dump(new_data, file, indent=4)

    # Download the json file of the data
    @render.download(filename="category_mappings.json")
    def download_json():
        yield json.dumps(category_mappings(), indent=4, sort_keys=True)

    @render.text
    def display_json():
        # Return a pretty dictionary string
        return json.dumps(category_mappings(), indent=4, sort_keys=True)
