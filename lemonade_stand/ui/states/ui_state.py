""""""

import reflex as rx


class UIState(rx.State):
    """State for UI interactions like sidebar toggling."""

    is_sidebar_collapsed: bool = False

    @rx.event
    def toggle_sidebar(self):
        """"""

        self.is_sidebar_collapsed = not self.is_sidebar_collapsed


class DateState(rx.State):
    """"""

    available_years: list[str] = ["2023", "2024", "2025", "2026"]
    available_months: list[str] = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    selected_year: str = ""
    selected_month: str = ""

    @rx.var
    def button_display_text(self) -> str:
        """Dynamically updates the text on the button surface."""
        if self.selected_month != "":
            return f"{self.selected_month} {self.selected_year}"
        elif self.selected_year != "":
            return self.selected_year
        else:
            return "All Time"

    @rx.event
    def set_year(self, year: str):
        """"""
        self.selected_year = year

    @rx.event
    def set_month(self, month: str):
        """"""
        self.selected_month = month


class ActivityState(rx.State):
    """"""

    activity_filter: str = "All"

    @rx.event
    def set_activity_filter(self, value: str):
        """Change the activity filter value."""
        self.activity_filter = value
