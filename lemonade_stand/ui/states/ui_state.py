""""""

import reflex as rx


class UIState(rx.State):
    """State for UI interactions like sidebar toggling."""

    is_sidebar_collapsed: bool = False

    @rx.event
    def toggle_sidebar(self):
        """"""

        self.is_sidebar_collapsed = not self.is_sidebar_collapsed
