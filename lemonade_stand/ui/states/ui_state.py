""""""

import reflex as rx


class UIState(rx.State):
    """State for UI interactions like sidebar toggling."""

    is_sidebar_collapsed: bool = False

    @rx.event
    def toggle_sidebar(self):
        """"""
        self.is_sidebar_collapsed = not self.is_sidebar_collapsed

    @rx.event
    def collapse_sidebar(self):
        """"""
        self.is_sidebar_collapsed = True


class ActivityState(rx.State):
    """"""

    activity_filter: str = "All"

    @rx.event
    def set_activity_filter(self, value: str):
        """Change the activity filter value."""
        self.activity_filter = value
