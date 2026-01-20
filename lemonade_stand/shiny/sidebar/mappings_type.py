"""
A user mapping configurations for the category
"""

import json
from pathlib import Path

import polars as pl
from faicons import icon_svg
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shiny.types import FileInfo

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
CONFIG_PATH = AppDir().types_config_path


@module.ui
def mappings_type_ui():
    """
    A UI module for the user-guide page
    """

    return ui.input_action_link(
        id="open_mappings",
        label="Types",
        style="margin: 0 0 0.5rem 1.2rem;",
        class_="sidebar-link items-top-left",
        icon=icon_svg("layer-group"),
    )


@module.server
def mappings_type_server(input, output, session):  # noqa: ARG001
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
                id="user_upload",
                label="File upload mappings",
                accept=[".json", ".csv"],
                multiple=False,
            ),
            ui.output_ui(id="confirm_upload"),
            ui.p("Manual input mappings"),
            ui.div(
                ui.input_action_button(
                    id="add_mapping", label="Add", class_="confirm-button"
                ),
                ui.span("𓃊", style="padding: 0.5rem 0.5rem 0.5rem 0.5rem;"),
                ui.span(
                    ui.input_text(id="key_mapping", label=None, placeholder="Type"),
                    ui.input_text(
                        id="value_mapping", label=None, placeholder="Category"
                    ),
                    class_="items-top-left",
                ),
                class_="items-top-left",
            ),
            ui.output_ui(id="confirm_override"),
            ui.div(
                ui.input_action_button(
                    id="delete_mapping", label="Delete", class_="confirm-button"
                ),
                ui.span("𓃊", style="padding: 0.5rem 0.5rem 0.5rem 0.5rem;"),
                ui.span(
                    ui.input_text(id="key_delete", label=None, placeholder="Type"),
                    ui.input_text(
                        id="value_delete", label=None, placeholder="Category"
                    ),
                    class_="items-top-left",
                ),
                class_="items-top-left",
            ),
            ui.output_ui(id="confirm_deletion"),
            ui.div(
                ui.download_button(
                    "download_json", "Download json", class_="download-button"
                ),
                class_="items-bottom-right",
            ),
            ui.output_text_verbatim(id="display_json", placeholder=True),
            ui.modal_button("Close", class_="space-items"),
            title="CATEGORY TYPE MAPPINGS",
            class_="modal-content",
            easy_close=True,
            footer=None,
            size="l",
        )

        # Unhide the modal
        ui.modal_show(mappings_modal)

    @render.ui
    @reactive.event(input.add_mapping)
    def confirm_override():
        category_input = input.key_mapping()
        substring_input = input.value_mapping()
        new_data = category_mappings.get().copy()
        current_keys = [
            x for x, y in category_mappings().items() if substring_input in y
        ]

        # Clear if the current mapping already exists
        if (category_input in current_keys) and substring_input in new_data.get(
            category_input, []
        ):
            return ui.div()

        if len(current_keys) > 0:
            LOGGER.info(
                "There exist a mapping with the provided substring value. Requesting confirmation..."
            )

            return ui.div(
                ui.p(
                    f"Substring '{substring_input}' already exists in '{current_keys[0]}' category. Would you like to override the current mapping? ",
                    class_="invalid-note",
                ),
                ui.input_radio_buttons(
                    id="confirm_add_mapping",
                    label=None,
                    choices=["yes", "no"],
                    selected="no",
                    inline=True,
                ),
                class_="items-top-left",
            )

        else:
            # If it's a new key, update immediately
            if not any(substring_input in y for _, y in new_data.items()):
                LOGGER.info("Adding new category mapping...")

                new_data[category_input] = new_data.get(category_input, []) + [
                    substring_input
                ]

                # Update reactive value
                category_mappings.set(new_data)

            return ui.span("Success!", class_="valid-note")

    @reactive.Effect(priority=-1)
    @reactive.event(input.confirm_add_mapping)
    def _():
        # Update after user confirms
        category_input = input.key_mapping()
        substring_input = input.value_mapping()
        new_data = category_mappings.get().copy()

        if input.confirm_add_mapping() == "yes":
            current_keys = [x for x, y in new_data.items() if substring_input in y]

            # Add redundancy check incase the current key-category doesn't exist
            if len(current_keys) > 0:
                LOGGER.info("Overriding old mapping")

                new_data[current_keys[0]] = [
                    x for x in new_data[current_keys[0]] if x != substring_input
                ]
                new_data[category_input] = new_data.get(category_input, []) + [
                    substring_input
                ]

                # Update reactive value
                category_mappings.set(new_data)

    @render.ui
    @reactive.event(input.delete_mapping)
    def confirm_deletion():
        delete_type = input.key_delete()
        delete_category = input.value_delete()
        new_data = category_mappings.get().copy()

        # Clear if the current mapping already exists
        if (delete_type not in new_data) and (delete_category == ""):
            LOGGER.info(
                "Transaction-Type does not exist. Cleaning up deletion messages..."
            )
            return ui.div()

        # Confirm that the category exists in the config
        if delete_type in new_data:
            category_list = new_data[delete_type]

            # Confirm that the substring exists in the category list
            if delete_category in category_list:
                LOGGER.info("Deleting category mapping...")

                # If category has more than one in list then drop only one
                if len(category_list) > 1:
                    new_data[delete_type] = [
                        x for x in category_list if x != delete_category
                    ]
                else:
                    new_data = {x: y for x, y in new_data.items() if x != delete_type}

                # Update the reactive value
                category_mappings.set(new_data)

                return ui.span("Success!", class_="valid-note")
            else:
                LOGGER.info(
                    "Category does not exist in Transaction-Type. Skipping category mapping deletion..."
                )

                return ui.span(
                    f"Category '{delete_category}' does not exist in Transaction-Type '{delete_type}'",
                    class_="invalid-note",
                )
        else:
            return ui.span(
                f"Transaction-Type '{delete_type}' does not exist",
                class_="invalid-note",
            )

    # A function to reactively update the local config file
    @reactive.Effect
    @reactive.event(category_mappings)
    def _():
        new_data = category_mappings()

        # Save current mappings to file
        with CONFIG_PATH.open("w") as file:
            json.dump(new_data, file, indent=4)

    # File upload confirmation
    @render.ui
    @reactive.event(input.user_upload)
    def confirm_upload():
        # Get the uploaded file list
        upload_files: list[FileInfo] | None = input.user_upload()

        # Conditionally process the files
        if upload_files is None:
            LOGGER.info("No user uploaded file uploaded. Skipping processing...")
            return ui.div()

        else:
            upload_path = Path(str(upload_files[0]["datapath"]))

            # Check the file type
            if upload_path.suffix == ".json":
                LOGGER.info("Reading user uploaded json file")

                with upload_path.open("r") as file:
                    uploaded_mappings = json.load(file)

            elif upload_path.suffix == ".csv":
                LOGGER.info("Reading user uploaded csv file")

                uploaded_df = pl.read_csv(
                    source=upload_path,
                    has_header=False,
                    separator=",",
                )
                uploaded_mappings = dict(uploaded_df.iter_rows())

            else:
                ui.span(
                    f"Application does not support files with extension '{upload_path.suffix}'. Please upload '.json' or '.csv' files.",
                    class_="invalid-note",
                )

            LOGGER.info("Setting up user mappings into mapping config")

            # Clean up the data and update reactive value
            uploaded_mappings = {
                x: (y if isinstance(y, list) else [y])
                for x, y in uploaded_mappings.items()
                if not isinstance(y, dict)  # Filter out nested dicts
            }

            category_mappings.set({**category_mappings(), **uploaded_mappings})

            # Return success message
            return ui.span(
                "Success! File mappings have been imported!",
                class_="valid-note",
            )

    # Download the json file of the data
    @render.download(filename="transaction_type_mappings.json")
    def download_json():
        LOGGER.info("Downloading mapping json file...")

        yield json.dumps(category_mappings(), indent=4, sort_keys=True)

    @render.text
    def display_json():
        LOGGER.info("Displaying json...")

        # Return a pretty dictionary string
        return json.dumps(category_mappings.get(), indent=4, sort_keys=True)
