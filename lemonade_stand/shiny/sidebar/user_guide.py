"""
A user guide configurations
"""

from pathlib import Path

from shiny import module
from shiny import reactive
from shiny import ui

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


@module.ui
def user_guide_ui():
    """
    A UI module for the user-guide page
    """

    return ui.input_action_link(
        "open_user_guide", "📄 User Guide", class_="sidebar-link"
    )


@module.server
def user_guide_server(input, output, session):  # noqa: ARG001
    """
    A server module for the user-guide page
    """

    @reactive.effect
    @reactive.event(input.open_user_guide)
    def _():
        # Set up the modal
        user_guide_modal = ui.modal(
            ui.h5("How to Run"),
            ui.br(),
            ui.output_text_verbatim(id="documentation", placeholder=False),
            ui.span(ui.modal_button("Close"), class_="items-centered space-items"),
            title="USER GUIDE",
            class_="modal-content",
            easy_close=True,
            footer=None,
            size="l",
        )

        # Unhide the modal
        ui.modal_show(user_guide_modal)
