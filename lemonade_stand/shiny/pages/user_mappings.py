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

    @reactive.Effect(priority=2)
    @reactive.event(input.open_mappings)
    def _():
        LOGGER.info("Displaying mappings modal...")

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
                    ui.input_text(id="key_mapping", label=None, placeholder="Category"),
                    ui.input_text(
                        id="value_mapping", label=None, placeholder="Value substring"
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
            ui.output_text_verbatim(id="display_json", placeholder=True),
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
    @reactive.event(input.add_mapping, input.confirm_add_mapping)
    def confirm_override():
        substring_input = input.value_mapping()
        current_key = [
            x for x, y in category_mappings().items() if substring_input in y
        ]

        if len(current_key) > 0:
            LOGGER.info(
                "There exist a mapping with the provided substring value. Requesting confirmation..."
            )

            return ui.div(
                ui.p(
                    f"Substring '{substring_input}' already exists in '{current_key[0]}' category. Would you like to override the current mapping? ",
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

    @reactive.Effect(priority=-1)
    @reactive.event(input.add_mapping)
    def _():
        category_input = input.key_mapping()
        substring_input = input.value_mapping()
        new_data = category_mappings.get().copy()

        # If it's a new key, update immediately
        if not any(substring_input in y for _, y in new_data.items()):
            LOGGER.info("Adding new category mapping...")

            new_data[category_input] = new_data.get(category_input, []) + [
                substring_input
            ]
            category_mappings.set(new_data)

            # Save to file
            with CONFIG_PATH.open("w") as file:
                json.dump(new_data, file, indent=4)

    @reactive.Effect(priority=-1)
    @reactive.event(input.confirm_add_mapping)
    def _():
        # Update after user confirms
        category_input = input.key_mapping()
        substring_input = input.value_mapping()
        new_data = category_mappings.get().copy()

        current_key = [x for x, y in new_data.items() if substring_input in y]

        # Add redundancy check incase the current key-category doesn't exist
        if len(current_key) > 0:
            LOGGER.info("Overriding old mapping")

            new_data[current_key[0]] = [
                x for x in new_data[current_key[0]] if x != substring_input
            ]
            new_data[category_input] = new_data.get(category_input, []) + [
                substring_input
            ]
            category_mappings.set(new_data)

            # Save to file
            with CONFIG_PATH.open("w") as file:
                json.dump(new_data, file, indent=4)

    # Download the json file of the data
    @render.download(filename="category_mappings.json")
    def download_json():
        LOGGER.info("Downloading mapping json file...")

        yield json.dumps(category_mappings(), indent=4, sort_keys=True)

    @render.text
    def display_json():
        LOGGER.info("Displaying json...")

        # Return a pretty dictionary string
        return json.dumps(category_mappings.get(), indent=4, sort_keys=True)
