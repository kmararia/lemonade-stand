""""""

import datetime
import logging
import uuid
from typing import TypedDict

import reflex as rx

from lemonade_stand.config import UserConfig
from lemonade_stand.data import get_data

from .utils import DataManager

USER_CONFIG = UserConfig()
DATA_CONFIG = DataManager(
    name="expenses", input_data=get_data(config=USER_CONFIG).expenses
)


class Budget(TypedDict):
    """"""

    id: str
    name: str
    type: str
    allocated_amount: float
    period: str


class ExpenseSplit(TypedDict):
    """"""

    category: str
    amount: float


class ExpenseComment(TypedDict):
    """"""

    id: str
    user: str
    avatar: str
    text: str
    timestamp: str


class ExpenseHistory(TypedDict):
    """"""

    action: str
    user: str
    timestamp: str
    note: str


class Expense(TypedDict):
    """"""

    id: str
    date: str
    description: str
    amount: float
    category: str
    payment_type: str
    location: list[str]
    exclude_flag: str

    recurring_flag: bool
    has_source_file: bool
    splits: list[ExpenseSplit]
    comments: list[ExpenseComment]
    history: list[ExpenseHistory]
    assigned_approver_id: str
    source_file: str


class ChartData(TypedDict):
    """"""

    name: str
    allocated: float
    spent: float


class BudgetStats(TypedDict):
    """"""

    id: str
    name: str
    type: str
    allocated_amount: float
    period: str
    spent: float
    remaining: float
    utilization: float
    health_color: str
    health_bg: str
    progress_color: str


class BudgetState(rx.State):
    """Core state for budget and expense data."""

    is_budget_modal_open: bool = False
    is_expense_modal_open: bool = False
    is_attachment_preview_open: bool = False
    active_expense_tab: str = "details"
    selected_expense_ids: list[str] = []
    attachment_zoom: int = 100
    new_comment_text: str = ""
    expense_search: str = ""
    expense_category_filter: str = "All"

    available_tags: list[str] = DATA_CONFIG.available_categories
    budgets: list[Budget] = DATA_CONFIG.budget_allocations
    expenses: list[Expense] = list(DATA_CONFIG.get_row_iterable)
    current_budget: Budget = DATA_CONFIG.current_allocation
    current_expense: Expense = DATA_CONFIG.current_row

    departments: list[str] = ["Marketing", "Engineering", "HR", "Sales", "Operations"]
    projects: list[str] = ["Office Renovation", "Website Redesign", "Q2 Hiring Push"]
    report_date_range: str = "Year to Date"
    warning_threshold: int = 75
    critical_threshold: int = 90

    @rx.var
    def total_budget(self) -> float:
        """"""

        return sum(b["allocated_amount"] for b in self.budgets)

    @rx.var
    def total_spent(self) -> float:
        """"""

        return sum(
            e["amount"] for e in self.expenses if e["exclude_flag"] != "Rejected"
        )

    @rx.var
    def remaining_budget(self) -> float:
        """"""

        return self.total_budget - self.total_spent

    @rx.var
    def utilization_percentage(self) -> float:
        """"""

        if self.total_budget == 0:
            return 0.0
        return round(self.total_spent / self.total_budget * 100, 1)

    @rx.var
    def budget_vs_actual_spend(self) -> list[ChartData]:
        """"""

        data = []
        for budget in self.budgets:
            category_spent = sum(
                e["amount"]
                for e in self.expenses
                if e["category"] == budget["name"] and e["exclude_flag"] != "Rejected"
            )
            data.append(
                {
                    "name": budget["name"],
                    "allocated": budget["allocated_amount"],
                    "spent": category_spent,
                }
            )
        return data

    @rx.var
    def budget_stats(self) -> list[BudgetStats]:
        """"""

        stats = []
        for b in self.budgets:
            spent = sum(
                e["amount"]
                for e in self.expenses
                if e["category"] == b["name"] and e["exclude_flag"]
            )
            total = b["allocated_amount"]
            utilization = (spent / total * 100) if total > 0 else 0.0
            color = (
                "red"
                if utilization > self.critical_threshold
                else "orange"
                if utilization > self.warning_threshold
                else "emerald"
            )

            stats.append(
                {
                    "name": b["name"],
                    "type": b["type"],
                    "allocated_amount": total,
                    "period": b["period"],
                    "spent": spent,
                    "remaining": total - spent,
                    "utilization": round(utilization, 1),
                    "health_color": f"text-{color}-500",
                    "health_bg": f"bg-{color}-50",
                    "progress_color": f"bg-{color}-500",
                }
            )

        return stats

    @rx.var
    def category_distribution(self) -> list[dict]:
        """Returns data for pie chart distribution."""
        distribution = {}
        for e in self.expenses:
            if e["exclude_flag"] == "Rejected":
                continue
            cat = e["category"]
            distribution[cat] = distribution.get(cat, 0) + e["amount"]
        return [
            {"name": k, "value": v} for i, (k, v) in enumerate(distribution.items())
        ]

    @rx.var
    def filtered_expenses(self) -> list[Expense]:
        """"""

        filtered = self.expenses
        if self.expense_category_filter != "All":
            filtered = [
                e for e in filtered if e["category"] == self.expense_category_filter
            ]
        if self.expense_search:
            search = self.expense_search.lower()
            filtered = [
                e
                for e in filtered
                if search in e["description"].lower() or search in e["category"].lower()
            ]
        return sorted(filtered, key=lambda x: x["date"], reverse=True)

    @rx.var
    def spending_forecast(self) -> list[dict]:
        """Returns forecast data for area chart based on actual expenses."""
        import calendar
        import datetime

        current_year = datetime.date.today().year
        monthly_data = {}
        for m in range(1, 13):
            month_name = calendar.month_abbr[m]
            monthly_data[month_name] = {"actual": 0, "projected": 0}
        for e in self.expenses:
            if e["exclude_flag"] == "Rejected":
                continue
            try:
                date_obj = e["date"]
                if date_obj.year == current_year:
                    month_name = date_obj.strftime("%b")
                    monthly_data[month_name]["actual"] += e["amount"]
            except Exception as e:
                logging.exception("Error processing spending forecast: %s", e)
                continue
        total_actual = sum(d["actual"] for d in monthly_data.values())
        months_with_data = len([d for d in monthly_data.values() if d["actual"] > 0])
        avg_spend = total_actual / max(1, months_with_data)
        current_month_idx = datetime.date.today().month
        result = []
        for i, m in enumerate(range(1, 13)):
            month_name = calendar.month_abbr[m]
            data_point = {"month": month_name, "actual": 0, "projected": 0}
            if i < current_month_idx:
                data_point["actual"] = monthly_data[month_name]["actual"]
                data_point["projected"] = monthly_data[month_name]["actual"]
            else:
                growth_factor = 1 + (i - current_month_idx) * 0.02
                data_point["actual"] = 0
                data_point["projected"] = round(avg_spend * growth_factor)
            result.append(data_point)
        return result

    @rx.var
    def department_comparison_data(self) -> list[dict]:
        """Returns data for department comparison bar chart."""
        data = []
        for b in self.budgets:
            if b["type"] == "Department":
                spent = sum(
                    e["amount"]
                    for e in self.expenses
                    if e["category"] == b["name"] and e["exclude_flag"] != "Rejected"
                )
                data.append(
                    {"name": b["name"], "Budget": b["allocated_amount"], "Spent": spent}
                )
        return sorted(data, key=lambda x: x["Spent"], reverse=True)

    @rx.event
    def open_add_budget_modal(self):
        """"""

        self.current_budget = {
            "id": "",
            "name": "",
            "type": "Department",
            "allocated_amount": 0.0,
            "period": "Annual",
        }
        self.is_budget_modal_open = True

    @rx.event
    def open_edit_budget_modal(self, budget: Budget):
        """"""

        self.current_budget = budget
        self.is_budget_modal_open = True

    @rx.event
    def close_budget_modal(self):
        """"""

        self.is_budget_modal_open = False

    @rx.event
    def update_current_budget(self, key: str, value: str):
        """"""

        if key == "allocated_amount":
            try:
                val = float(value)
                self.current_budget["allocated_amount"] = val
            except ValueError as e:
                logging.exception("Error converting allocated_amount to float: %s", e)
        else:
            self.current_budget[key] = value

    @rx.event
    def save_budget(self):
        """"""
        if self.current_budget["name"] == "":
            return
        if self.current_budget["id"]:
            self.budgets = [
                b if b["id"] != self.current_budget["id"] else self.current_budget
                for b in self.budgets
            ]
        else:
            new_budget = self.current_budget.copy()
            new_budget["id"] = str(uuid.uuid4())
            self.budgets.append(new_budget)
        self.close_budget_modal()

    @rx.event
    def delete_budget(self, id: str):
        """"""

        self.budgets = [b for b in self.budgets if b["id"] != id]

    @rx.event
    def open_add_expense_modal(self):
        """"""

        default_category = self.budgets[0]["name"] if self.budgets else ""
        self.current_expense = {
            "id": "",
            "date": datetime.date.today().isoformat(),
            "category": default_category,
            "amount": 0.0,
            "payment_type": "Credit Card",
            "description": "",
            "exclude_flag": False,
            "recurring_flag": False,
            "has_source_file": False,
            "tags": [],
            "splits": [],
            "comments": [],
            "history": [],
            "assigned_approver_id": "",
            "attachment_url": "",
        }
        self.active_expense_tab = "details"
        self.is_expense_modal_open = True

    @rx.event
    def open_edit_expense_modal(self, expense: Expense):
        """"""

        if "splits" not in expense:
            expense["splits"] = []
        if "comments" not in expense:
            expense["comments"] = []
        if "history" not in expense:
            expense["history"] = []
        if "assigned_approver_id" not in expense:
            expense["assigned_approver_id"] = ""
        if "attachment_url" not in expense:
            expense["attachment_url"] = ""
        self.current_expense = expense
        self.active_expense_tab = "details"
        self.is_expense_modal_open = True

    @rx.event
    def close_expense_modal(self):
        """"""
        self.is_expense_modal_open = False
        self.new_comment_text = ""

    @rx.event
    def set_active_expense_tab(self, tab: str):
        """"""

        self.active_expense_tab = tab

    @rx.event
    def update_current_expense(self, key: str, value: str):
        """"""

        if key == "amount":
            try:
                val = float(value)
                self.current_expense["amount"] = val
            except ValueError as e:
                logging.exception("Error converting amount to float: %s", e)
        else:
            self.current_expense[key] = value

    @rx.event
    def duplicate_expense(self, expense: Expense):
        """"""

        new_expense = expense.copy()
        new_expense["id"] = str(uuid.uuid4())
        new_expense["description"] = f"Copy of {expense['description']}"
        new_expense["date"] = datetime.date.today().isoformat()
        new_expense["exclude_flag"] = "Pending"
        new_expense["recurring_flag"] = False
        new_expense["history"] = []
        new_expense["comments"] = []
        self.expenses.insert(0, new_expense)
        return rx.toast("Expense duplicated successfully")

    @rx.event
    def add_expense_comment(self):
        """"""

        if not self.new_comment_text:
            return
        comment: ExpenseComment = {
            "id": str(uuid.uuid4()),
            "user": "Alex Finance",
            "avatar": "Felix",
            "text": self.new_comment_text,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.current_expense["comments"].append(comment)
        self.new_comment_text = ""

    @rx.event
    def set_new_comment_text(self, text: str):
        """"""

        self.new_comment_text = text

    @rx.event
    def add_split(self):
        """"""

        default_category = self.budgets[0]["name"] if self.budgets else ""
        self.current_expense["splits"].append(
            {"category": default_category, "amount": 0.0}
        )

    @rx.event
    def remove_split(self, index: int):
        """"""

        if 0 <= index < len(self.current_expense["splits"]):
            self.current_expense["splits"].pop(index)

    @rx.event
    def update_split(self, index: int, key: str, value: str):
        """"""

        if 0 <= index < len(self.current_expense["splits"]):
            if key == "amount":
                try:
                    self.current_expense["splits"][index][key] = float(value)
                except ValueError as e:
                    logging.exception("Error converting split amount to float: %s", e)
            else:
                self.current_expense["splits"][index][key] = value

    @rx.event
    def open_attachment_preview(self):
        """"""

        if self.current_expense["attachment_url"]:
            self.attachment_zoom = 100
            self.is_attachment_preview_open = True
        elif self.current_expense["has_source_file"]:
            self.current_expense["attachment_url"] = (
                "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=1000"
            )
            self.attachment_zoom = 100
            self.is_attachment_preview_open = True
        else:
            rx.toast("No attachment to preview")

    @rx.event
    def zoom_in(self):
        """"""

        if self.attachment_zoom < 300:
            self.attachment_zoom += 25

    @rx.event
    def zoom_out(self):
        """"""

        if self.attachment_zoom > 25:
            self.attachment_zoom -= 25

    @rx.event
    def close_attachment_preview(self):
        """"""

        self.is_attachment_preview_open = False

    @rx.event
    def save_expense(self):
        """"""

        if self.current_expense["description"] == "":
            return
        self.current_expense["history"].append(
            {
                "action": "Updated",
                "user": "Alex Finance",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "note": "Expense details updated",
            }
        )
        if self.current_expense["id"]:
            self.expenses = [
                e if e["id"] != self.current_expense["id"] else self.current_expense
                for e in self.expenses
            ]
        else:
            new_expense = self.current_expense.copy()
            new_expense["id"] = str(uuid.uuid4())
            new_expense["history"].append(
                {
                    "action": "Created",
                    "user": "Alex Finance",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": "Initial submission",
                }
            )
            self.expenses.append(new_expense)
        self.close_expense_modal()

    @rx.event
    def delete_expense(self, id: str):
        """"""

        self.expenses = [e for e in self.expenses if e["id"] != id]
        if self.is_expense_modal_open and self.current_expense["id"] == id:
            self.is_expense_modal_open = False
            return rx.toast("Expense deleted.")

    @rx.event
    def set_expense_search(self, value: str):
        """"""

        self.expense_search = value

    @rx.event
    def set_expense_category_filter(self, value: str):
        """"""

        self.expense_category_filter = value

    @rx.event
    def set_report_date_range(self, value: str):
        """"""

        self.report_date_range = value

    @rx.event
    def set_warning_threshold(self, value: float):
        """"""

        try:
            self.warning_threshold = float(value)
        except ValueError as e:
            logging.exception("Error setting warning threshold: %s", e)

    @rx.event
    def set_critical_threshold(self, value: float):
        """"""

        try:
            self.critical_threshold = float(value)
        except ValueError as e:
            logging.exception("Error setting critical threshold: %s", e)

    @rx.event
    def add_department(self, name: str):
        """"""

        if name and name not in self.departments:
            self.departments.append(name)

    @rx.event
    def remove_department(self, name: str):
        """"""

        self.departments = [d for d in self.departments if d != name]

    @rx.event
    def add_project(self, name: str):
        """"""

        if name and name not in self.projects:
            self.projects.append(name)

    @rx.event
    def remove_project(self, name: str):
        """"""

        self.projects = [p for p in self.projects if p != name]

    @rx.event
    def toggle_expense_selection(self, id: str):
        """"""

        if id in self.selected_expense_ids:
            self.selected_expense_ids.remove(id)
        else:
            self.selected_expense_ids.append(id)

    @rx.event
    def toggle_all_expenses(self):
        """"""

        if len(self.selected_expense_ids) == len(self.filtered_expenses):
            self.selected_expense_ids = []
        else:
            self.selected_expense_ids = [e["id"] for e in self.filtered_expenses]

    @rx.event
    def approve_selected_expenses(self):
        """"""

        for e in self.expenses:
            if e["id"] in self.selected_expense_ids:
                e["exclude_flag"] = "Approved"
        self.selected_expense_ids = []
        return rx.toast("Selected expenses approved.")

    @rx.event
    def reject_selected_expenses(self):
        """"""

        for e in self.expenses:
            if e["id"] in self.selected_expense_ids:
                e["exclude_flag"] = "Rejected"
        self.selected_expense_ids = []
        return rx.toast("Selected expenses rejected.")

    @rx.event
    def delete_selected_expenses(self):
        """"""

        self.expenses = [
            e for e in self.expenses if e["id"] not in self.selected_expense_ids
        ]
        self.selected_expense_ids = []
        return rx.toast("Selected expenses deleted.")

    @rx.event
    def export_selected_expenses(self):
        """"""

        self.selected_expense_ids = []
        return rx.toast("Exporting selected expenses...", duration=3000)

    @rx.event
    def export_report_pdf(self):
        """"""

        return rx.toast(
            "Generating PDF report... Download will start shortly.", duration=3000
        )

    @rx.event
    def add_tag_to_current_expense(self, tag: str):
        """"""

        if tag and tag not in self.current_expense["tags"]:
            self.current_expense["tags"].append(tag)

    @rx.event
    def remove_tag_from_current_expense(self, tag: str):
        """"""

        self.current_expense["tags"] = [
            t for t in self.current_expense["tags"] if t != tag
        ]

    @rx.event
    def toggle_current_expense_attachment(self, checked: bool):
        """"""

        self.current_expense["has_source_file"] = checked
