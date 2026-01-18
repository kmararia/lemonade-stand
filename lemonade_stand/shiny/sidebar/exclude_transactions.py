"""
A user mapping configurations for the category
"""

import json
from pathlib import Path

import polars as pl
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shiny.types import FileInfo

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
CONFIG_PATH = AppDir().exclusions_config_path


@module.ui
def exclude_ui():
    """
    A UI module for the transactions to exclude
    """

    return ui.input_action_link(
        "open_mappings",
        "🗑️ Exclude transactions",
        class_="sidebar-link",
    )


@module.server
def exclude_server(input, output, session):  # noqa: ARG001
    """
    A server module for the transactions to exclude
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
                label="File mapping uploads",
                accept=[".json", ".csv"],
                multiple=False,
            ),
            ui.output_ui(id="confirm_upload"),
            ui.p("Manual input mappings"),
            ui.div(
                ui.input_action_button(
                    id="add_exclusion",
                    label="Add",
                    style="display: flex; justify-content: center; align-items: center; max-height: 2.3rem;",
                ),
                ui.span("𓃊", style="padding: 0.5rem 0.5rem 0.5rem 0.5rem;"),
                ui.input_text(
                    id="key_exclude", label=None, placeholder="Exclude transaction"
                ),
                style="display: flex; justify-content: flex-start; gap: 0.5rem;",
            ),
            ui.output_ui(id="confirm_addition"),
            ui.div(
                ui.input_action_button(
                    id="delete_exclusion",
                    label="Delete",
                    style="display: flex; justify-content: center; align-items: center; max-height: 2.3rem; max-width: 5.6rem;",
                ),
                ui.span("𓃊", style="padding: 0.5rem 0.5rem 0.5rem 0.5rem;"),
                ui.input_text(
                    id="key_delete", label=None, placeholder="Delete exclusion"
                ),
                style="display: flex; justify-content: flex-start; gap: 0.5rem;",
            ),
            ui.output_ui(id="confirm_deletion"),
            ui.div(
                ui.download_button(
                    "download_json", "Download json", class_="download-button"
                ),
                style="display: flex; justify-content: flex-end; align-items: center;",
            ),
            ui.output_text_verbatim(id="display_json", placeholder=True),
            size="l",
            easy_close=True,
            footer=ui.modal_button("Close"),
            title="EXCLUDE TRANSACTIONS",
            class_="modal-content",
        )

        # Unhide the modal
        ui.modal_show(mappings_modal)

    @render.ui
    @reactive.event(input.add_exclusion)
    def confirm_addition():
        exclude_input = input.key_exclude()
        old_data = category_mappings().get("exclude", [])
        new_data = old_data.copy()

        # Clear if the current mapping already exists
        if exclude_input in new_data:
            return ui.div()

        if exclude_input in old_data:
            LOGGER.info("Transaction exists in exclusion list. Displaying note...")
            return ui.p(
                "Transaction already exists in the exclusion list",
                class_="login-invalid-note",
            )

        else:
            LOGGER.info("Adding new exclusion transaction...")
            category_mappings.set({"exclude": (new_data + [exclude_input])})

            return ui.span(
                "Success!", class_="login-valid-note", style="margin-bottom: 1rem;"
            )

    @render.ui
    @reactive.event(input.delete_exclusion)
    def confirm_deletion():
        delete_input = input.key_delete()
        old_data = category_mappings().get("exclude", [])

        # Clear if the current mapping already exists
        if (delete_input not in old_data) or delete_input.strip() == "":
            LOGGER.info(
                "Exclusion transaction does not exist. Cleaning up deletion messages..."
            )
            return ui.div()

        # Confirm that the substring exists in the list
        if delete_input in old_data:
            LOGGER.info("Deleting category mapping...")

            category_mappings.set(
                {"exclude": [x for x in old_data if x != delete_input]}
            )

            return ui.span(
                "Success!", class_="login-valid-note", style="margin-bottom: 1rem;"
            )
        else:
            LOGGER.info("Exclusion transaction does not exist. Skipping deletion...")

            return ui.span(
                f"Exclusion transaction '{delete_input}' does not exist list",
                class_="login-invalid-note",
            )

    @reactive.Effect
    def _():
        """
        A function to reactively update the local config file
        """
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
                    uploaded_exclusions = json.load(file)

            elif upload_path.suffix == ".csv":
                LOGGER.info("Reading user uploaded csv file")

                uploaded_df = pl.read_csv(
                    source=upload_path,
                    has_header=False,
                    separator=",",
                )
                uploaded_exclusions = list(uploaded_df.iter_rows())

            else:
                ui.span(
                    f"Application does not support files with extension '{upload_path.suffix}'. Please upload '.json' or '.csv' files.",
                    class_="login-invalid-note",
                    style="margin-bottom: 1rem;",
                )

            LOGGER.info("Setting up user mappings into mapping config")

            # Clean up the data and update reactive value
            if isinstance(uploaded_exclusions, list):
                pass
            elif isinstance(uploaded_exclusions, dict):
                if any(x.lower() == "exclude" for x in uploaded_exclusions):
                    uploaded_exclusions = uploaded_exclusions.get("exclude")
                else:
                    return ui.div(
                        ui.span(
                            "Key 'exclude' does not exist in the uploaded file. Please reupload with the following format:"
                        ),
                        ui.span("'exclude': [transactions strings to exclude]"),
                        class_="login-invalid-note",
                    )
            else:
                return ui.span(
                    "Uploaded file does not have an object of type 'list' or 'dict' at the highest level",
                    class_="login-invalid-note",
                )

            current_exclusions = category_mappings().get("exclude", [])
            category_mappings.set(
                {"exclude": (current_exclusions + uploaded_exclusions)}
            )

            # Return success message
            return ui.span(
                "Success! File mappings have been imported!",
                class_="login-valid-note",
                style="margin-bottom: 1rem;",
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
