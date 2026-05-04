""""""

import datetime
import logging
import uuid
from typing import TypedDict

import reflex as rx


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
    category: str
    amount: float
    payment_method: str
    description: str
    approval_status: str
    recurring_frequency: str
    has_attachment: bool
    tags: list[str]
    splits: list[ExpenseSplit]
    comments: list[ExpenseComment]
    history: list[ExpenseHistory]
    assigned_approver_id: str
    attachment_url: str


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
    new_comment_text: str = ""
    attachment_zoom: int = 100
    current_budget: Budget = {
        "id": "",
        "name": "",
        "type": "Department",
        "allocated_amount": 0.0,
        "period": "Annual",
    }
    current_expense: Expense = {
        "id": "",
        "date": "",
        "category": "",
        "amount": 0.0,
        "payment_method": "Credit Card",
        "description": "",
        "approval_status": "Pending",
        "recurring_frequency": "One-time",
        "has_attachment": False,
        "tags": [],
        "splits": [],
        "comments": [],
        "history": [],
        "assigned_approver_id": "",
        "attachment_url": "",
    }
    selected_expense_ids: list[str] = []
    available_tags: list[str] = [
        "Travel",
        "Software",
        "Equipment",
        "Food",
        "Office",
        "Client",
        "Internal",
    ]
    expense_search: str = ""
    expense_category_filter: str = "All"
    budgets: list[Budget] = [
        {
            "id": "b1",
            "name": "Marketing",
            "type": "Department",
            "allocated_amount": 50000.0,
            "period": "Annual",
        },
        {
            "id": "b2",
            "name": "Engineering",
            "type": "Department",
            "allocated_amount": 120000.0,
            "period": "Annual",
        },
        {
            "id": "b3",
            "name": "Office Renovation",
            "type": "Project",
            "allocated_amount": 15000.0,
            "period": "One-time",
        },
        {
            "id": "b4",
            "name": "Software Licenses",
            "type": "Category",
            "allocated_amount": 8000.0,
            "period": "Annual",
        },
        {
            "id": "b5",
            "name": "Team Events",
            "type": "Category",
            "allocated_amount": 5000.0,
            "period": "Annual",
        },
        {
            "id": "b6",
            "name": "HR",
            "type": "Department",
            "allocated_amount": 30000.0,
            "period": "Annual",
        },
        {
            "id": "b7",
            "name": "Sales",
            "type": "Department",
            "allocated_amount": 80000.0,
            "period": "Annual",
        },
        {
            "id": "b8",
            "name": "Operations",
            "type": "Department",
            "allocated_amount": 45000.0,
            "period": "Annual",
        },
        {
            "id": "b9",
            "name": "Website Redesign",
            "type": "Project",
            "allocated_amount": 25000.0,
            "period": "One-time",
        },
        {
            "id": "b10",
            "name": "Q2 Hiring Push",
            "type": "Project",
            "allocated_amount": 12000.0,
            "period": "Q2",
        },
    ]
    expenses: list[Expense] = [
        {
            "id": "e1",
            "date": "2024-01-15",
            "category": "Software Licenses",
            "amount": 5000.0,
            "payment_method": "Bank Transfer",
            "description": "Annual Enterprise License Renewal",
            "approval_status": "Approved",
            "recurring_frequency": "Annual",
            "has_attachment": True,
            "tags": ["Software", "Internal"],
            "splits": [],
            "comments": [
                {
                    "id": "c1",
                    "user": "Sarah Marketing",
                    "avatar": "Sarah",
                    "text": "Approved for annual renewal.",
                    "timestamp": "2024-01-16 10:00",
                }
            ],
            "history": [
                {
                    "action": "Approved",
                    "user": "Sarah Marketing",
                    "timestamp": "2024-01-16 10:00",
                    "note": "Annual renewal",
                }
            ],
            "assigned_approver_id": "",
            "attachment_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&q=80&w=1000",
        },
        {
            "id": "e2",
            "date": "2024-01-20",
            "category": "Marketing",
            "amount": 1200.0,
            "payment_method": "Credit Card",
            "description": "Q1 Planning Workshop",
            "approval_status": "Approved",
            "recurring_frequency": "One-time",
            "has_attachment": False,
            "tags": ["Internal"],
            "splits": [],
            "comments": [],
            "history": [],
            "assigned_approver_id": "",
            "attachment_url": "",
        },
        {
            "id": "e3",
            "date": "2024-01-25",
            "category": "Engineering",
            "amount": 800.0,
            "payment_method": "Credit Card",
            "description": "DevOps Tools",
            "approval_status": "Approved",
        },
        {
            "id": "e4",
            "date": "2024-02-05",
            "category": "Engineering",
            "amount": 3500.0,
            "payment_method": "Bank Transfer",
            "description": "AWS Cloud Services - Jan",
            "approval_status": "Approved",
        },
        {
            "id": "e5",
            "date": "2024-02-10",
            "category": "Sales",
            "amount": 1500.0,
            "payment_method": "Credit Card",
            "description": "Client Visit - Chicago",
            "approval_status": "Approved",
        },
        {
            "id": "e6",
            "date": "2024-02-14",
            "category": "Team Events",
            "amount": 800.0,
            "payment_method": "Reimbursement",
            "description": "Valentine's Day Team Lunch",
            "approval_status": "Approved",
        },
        {
            "id": "e7",
            "date": "2024-02-28",
            "category": "Operations",
            "amount": 450.0,
            "payment_method": "Credit Card",
            "description": "Office Supplies Restock",
            "approval_status": "Approved",
        },
        {
            "id": "e8",
            "date": "2024-03-01",
            "category": "Marketing",
            "amount": 1200.5,
            "payment_method": "Credit Card",
            "description": "Q1 Ad Campaign Launch",
            "approval_status": "Approved",
        },
        {
            "id": "e9",
            "date": "2024-03-02",
            "category": "Engineering",
            "amount": 3400.0,
            "payment_method": "Bank Transfer",
            "description": "AWS Cloud Services - Feb",
            "approval_status": "Approved",
        },
        {
            "id": "e10",
            "date": "2024-03-05",
            "category": "Office Renovation",
            "amount": 850.0,
            "payment_method": "Invoice",
            "description": "New Ergonomic Chairs",
            "approval_status": "Approved",
        },
        {
            "id": "e11",
            "date": "2024-03-10",
            "category": "HR",
            "amount": 2500.0,
            "payment_method": "Invoice",
            "description": "Recruitment Agency Fee",
            "approval_status": "Pending",
        },
        {
            "id": "e12",
            "date": "2024-03-15",
            "category": "Sales",
            "amount": 3200.0,
            "payment_method": "Credit Card",
            "description": "Q1 Sales Conference Tickets",
            "approval_status": "Approved",
        },
        {
            "id": "e13",
            "date": "2024-03-20",
            "category": "Engineering",
            "amount": 2100.0,
            "payment_method": "Credit Card",
            "description": "New Test Devices",
            "approval_status": "Rejected",
        },
        {
            "id": "e14",
            "date": "2024-04-02",
            "category": "Marketing",
            "amount": 8000.0,
            "payment_method": "Invoice",
            "description": "Q2 Media Buy",
            "approval_status": "Approved",
        },
        {
            "id": "e15",
            "date": "2024-04-05",
            "category": "Engineering",
            "amount": 3600.0,
            "payment_method": "Bank Transfer",
            "description": "AWS Cloud Services - Mar",
            "approval_status": "Approved",
        },
        {
            "id": "e16",
            "date": "2024-04-10",
            "category": "Website Redesign",
            "amount": 5000.0,
            "payment_method": "Bank Transfer",
            "description": "Design Agency Deposit",
            "approval_status": "Approved",
        },
        {
            "id": "e17",
            "date": "2024-04-15",
            "category": "Q2 Hiring Push",
            "amount": 2000.0,
            "payment_method": "Credit Card",
            "description": "LinkedIn Job Slots",
            "approval_status": "Approved",
        },
        {
            "id": "e18",
            "date": "2024-04-22",
            "category": "Operations",
            "amount": 1200.0,
            "payment_method": "Invoice",
            "description": "HVAC Maintenance",
            "approval_status": "Pending",
        },
        {
            "id": "e19",
            "date": "2024-05-03",
            "category": "Engineering",
            "amount": 4000.0,
            "payment_method": "Bank Transfer",
            "description": "AWS Cloud Services - Apr",
            "approval_status": "Approved",
        },
        {
            "id": "e20",
            "date": "2024-05-10",
            "category": "HR",
            "amount": 1500.0,
            "payment_method": "Credit Card",
            "description": "Manager Training Workshop",
            "approval_status": "Approved",
        },
        {
            "id": "e21",
            "date": "2024-05-15",
            "category": "Website Redesign",
            "amount": 8000.0,
            "payment_method": "Bank Transfer",
            "description": "Development Milestone 1",
            "approval_status": "Approved",
        },
        {
            "id": "e22",
            "date": "2024-05-20",
            "category": "Marketing",
            "amount": 450.0,
            "payment_method": "Reimbursement",
            "description": "Client Gifts",
            "approval_status": "Rejected",
        },
        {
            "id": "e23",
            "date": "2024-06-01",
            "category": "Team Events",
            "amount": 1200.0,
            "payment_method": "Credit Card",
            "description": "Summer Team Outing",
            "approval_status": "Pending",
        },
        {
            "id": "e24",
            "date": "2024-06-05",
            "category": "Engineering",
            "amount": 4200.0,
            "payment_method": "Bank Transfer",
            "description": "AWS Cloud Services - May",
            "approval_status": "Approved",
        },
        {
            "id": "e25",
            "date": "2024-06-12",
            "category": "Sales",
            "amount": 4000.0,
            "payment_method": "Credit Card",
            "description": "Annual Client Dinner",
            "approval_status": "Approved",
        },
        {
            "id": "e26",
            "date": "2024-06-25",
            "category": "Office Renovation",
            "amount": 5500.0,
            "payment_method": "Invoice",
            "description": "Painting and Flooring",
            "approval_status": "Approved",
        },
        {
            "id": "e27",
            "date": "2024-06-28",
            "category": "Q2 Hiring Push",
            "amount": 3500.0,
            "payment_method": "Invoice",
            "description": "Headhunter Success Fee",
            "approval_status": "Pending",
        },
    ]
    departments: list[str] = ["Marketing", "Engineering", "HR", "Sales", "Operations"]
    projects: list[str] = ["Office Renovation", "Website Redesign", "Q2 Hiring Push"]
    warning_threshold: int = 75
    critical_threshold: int = 90
    report_date_range: str = "Year to Date"

    @rx.var
    def total_budget(self) -> float:
        """"""

        return sum(b["allocated_amount"] for b in self.budgets)

    @rx.var
    def total_spent(self) -> float:
        """"""

        return sum(
            e["amount"] for e in self.expenses if e["approval_status"] != "Rejected"
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
    def budget_health_color(self) -> str:
        """Returns a tailwind color class based on budget health."""
        if self.utilization_percentage > self.critical_threshold:
            return "text-red-600"
        elif self.utilization_percentage > self.warning_threshold:
            return "text-orange-500"
        return "text-emerald-600"

    @rx.var
    def budget_health_bg(self) -> str:
        """Returns a tailwind bg class based on budget health."""
        if self.utilization_percentage > self.critical_threshold:
            return "bg-red-100"
        elif self.utilization_percentage > self.warning_threshold:
            return "bg-orange-100"
        return "bg-emerald-100"

    @rx.var
    def budget_vs_actual_data(self) -> list[ChartData]:
        """"""

        data = []
        for budget in self.budgets:
            category_spent = sum(
                e["amount"]
                for e in self.expenses
                if e["category"] == budget["name"]
                and e["approval_status"] != "Rejected"
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
                if e["category"] == b["name"] and e["approval_status"] != "Rejected"
            )
            total = b["allocated_amount"]
            utilization = spent / total * 100 if total > 0 else 0.0
            stats.append(
                {
                    "id": b["id"],
                    "name": b["name"],
                    "type": b["type"],
                    "allocated_amount": total,
                    "period": b["period"],
                    "spent": spent,
                    "remaining": total - spent,
                    "utilization": round(utilization, 1),
                    "health_color": "text-red-600"
                    if utilization > self.critical_threshold
                    else "text-orange-500"
                    if utilization > self.warning_threshold
                    else "text-emerald-600",
                    "health_bg": "bg-red-50"
                    if utilization > self.critical_threshold
                    else "bg-orange-50"
                    if utilization > self.warning_threshold
                    else "bg-emerald-50",
                    "progress_color": "bg-red-600"
                    if utilization > self.critical_threshold
                    else "bg-orange-500"
                    if utilization > self.warning_threshold
                    else "bg-emerald-600",
                }
            )
        return stats

    @rx.var
    def pending_approvals_count(self) -> int:
        """Returns the count of expenses pending approval."""
        return len([e for e in self.expenses if e["approval_status"] == "Pending"])

    @rx.var
    def category_distribution(self) -> list[dict]:
        """Returns data for pie chart distribution."""
        distribution = {}
        for e in self.expenses:
            if e["approval_status"] == "Rejected":
                continue
            cat = e["category"]
            distribution[cat] = distribution.get(cat, 0) + e["amount"]
        return [
            {"name": k, "value": v} for i, (k, v) in enumerate(distribution.items())
        ]

    @rx.var
    def monthly_trends(self) -> list[dict]:
        """Returns data for line chart trends."""
        trends = {}
        all_categories = set()
        for e in self.expenses:
            if e["approval_status"] == "Rejected":
                continue
            try:
                date_obj = datetime.datetime.strptime(e["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%b")
                if month_key not in trends:
                    trends[month_key] = {"name": month_key}
                cat = e["category"]
                all_categories.add(cat)
                trends[month_key][cat] = trends[month_key].get(cat, 0) + e["amount"]
            except Exception as e:
                logging.exception("Error processing expense date: %s", e)
                continue
        months_order = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        result = []
        for m in months_order:
            if m in trends:
                for cat in all_categories:
                    if cat not in trends[m]:
                        trends[m][cat] = 0
                result.append(trends[m])
        return result

    @rx.var
    def top_spending_category(self) -> str:
        """"""

        if not self.category_distribution:
            return "None"
        return max(self.category_distribution, key=lambda x: x["value"])["name"]

    @rx.var
    def current_split_total(self) -> float:
        """"""

        return sum(s["amount"] for s in self.current_expense["splits"])

    @rx.var
    def split_difference(self) -> float:
        """"""

        return self.current_expense["amount"] - self.current_split_total

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
            if e["approval_status"] == "Rejected":
                continue
            try:
                date_obj = datetime.datetime.strptime(e["date"], "%Y-%m-%d")
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
                    if e["category"] == b["name"] and e["approval_status"] != "Rejected"
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
            "payment_method": "Credit Card",
            "description": "",
            "approval_status": "Pending",
            "recurring_frequency": "One-time",
            "has_attachment": False,
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
        new_expense["approval_status"] = "Pending"
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
        elif self.current_expense["has_attachment"]:
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
                e["approval_status"] = "Approved"
        self.selected_expense_ids = []
        return rx.toast("Selected expenses approved.")

    @rx.event
    def reject_selected_expenses(self):
        """"""

        for e in self.expenses:
            if e["id"] in self.selected_expense_ids:
                e["approval_status"] = "Rejected"
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

        self.current_expense["has_attachment"] = checked
