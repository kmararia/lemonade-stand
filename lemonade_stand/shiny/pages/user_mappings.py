"""
A user guide configurations
"""

import json
import pprint
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
                label="Upload mapping file",
                accept=[".json", ".csv"],
                multiple=False,
            ),
            ui.p("Manual input mappings"),
            ui.div(
                ui.input_text(
                    id="key_mapping", label=None, placeholder="Key substring"
                ),
                ui.input_text(
                    id="value_mapping", label=None, placeholder="Category to map to"
                ),
                ui.input_action_button(
                    id="add_mapping",
                    label="Add",
                    style="display: flex; justify-content: center; align-items: center; max-height: 2.3rem; margin-left: 0.5rem;",
                ),
                style="display: flex; justify-content: flex-start; gap: 0.5rem; margin-bottom: 1rem;",
            ),
            ui.output_text_verbatim(id="display_json", placeholder=False),
            size="l",
            easy_close=True,
            footer=ui.modal_button("Close"),
            title="USER MAPPINGS",
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(mappings_modal)

    @render.text
    @reactive.event(category_mappings)
    def display_json():
        # Save into a dict
        mapping_dict = category_mappings()

        # Dump configurations into file
        with CONFIG_PATH.open("w") as file:
            json.dump(mapping_dict, file, indent=4)

        # Return a pretty the dictionary string
        return pprint.pformat(mapping_dict)
