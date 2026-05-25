""""""

import csv
import io
from datetime import datetime

import reflex as rx


class SettingsState(rx.State):
    """State for app settings and preferences."""

    notifications_email: bool = True
    notifications_dashboard: bool = True
    notifications_weekly: bool = False
    currency_format: str = "USD ($)"
    date_format: str = "MM/DD/YYYY"
    new_department_input: str = ""
    new_project_input: str = ""

    @rx.event
    def toggle_notifications_email(self, val: bool):
        """"""

        self.notifications_email = val

    @rx.event
    def toggle_notifications_dashboard(self, val: bool):
        """"""

        self.notifications_dashboard = val

    @rx.event
    def toggle_notifications_weekly(self, val: bool):
        """"""

        self.notifications_weekly = val

    @rx.event
    def set_currency_format(self, val: str):
        """"""

        self.currency_format = val

    @rx.event
    def set_date_format(self, val: str):
        """"""

        self.date_format = val

    @rx.event
    def set_new_department_input(self, val: str):
        """"""

        self.new_department_input = val

    @rx.event
    def set_new_project_input(self, val: str):
        """"""

        self.new_project_input = val

    @rx.event
    async def add_department(self):
        """"""

        from lemonade_stand.ui.states.budget_state import BudgetState

        budget_state = await self.get_state(BudgetState)
        budget_state.add_department(self.new_department_input)
        self.new_department_input = ""

    @rx.event
    async def add_project(self):
        """"""

        from lemonade_stand.ui.states.budget_state import BudgetState

        budget_state = await self.get_state(BudgetState)
        budget_state.add_project(self.new_project_input)
        self.new_project_input = ""

    @rx.event
    async def export_data(self):
        """"""

        from lemonade_stand.ui.states.budget_state import BudgetState

        budget_state = await self.get_state(BudgetState)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Date",
                "Category",
                "Description",
                "Amount",
                "Payment Method",
                "Status",
                "Recurring",
            ]
        )
        for expense in budget_state.expenses:
            writer.writerow(
                [
                    expense["date"],
                    expense["category"],
                    expense["description"],
                    expense["amount"],
                    expense["payment_type"],
                    expense["exclude_flag"],
                    expense.get("recurring_flag", False),
                ]
            )
        csv_content = output.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return rx.download(
            data=csv_content, filename=f"budget_track_export_{timestamp}.csv"
        )

    @rx.event
    def save_settings(self):
        """"""

        return rx.toast("Settings saved successfully.", duration=3000)
