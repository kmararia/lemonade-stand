""" """

import typing
from dataclasses import dataclass
from dataclasses import field

import reflex as rx

from lemonade_stand.config import UserConfig
from lemonade_stand.data import get_data

from .utils import DataManager

USER_CONFIG = UserConfig()
DATA_CONFIG = DataManager(
    name="expenses", input_data=get_data(config=USER_CONFIG).expenses
)


@dataclass
class Budget:
    """"""

    name: str
    type: str
    allocated_amount: float
    period: str


@dataclass
class ExpenseSplit:
    """"""

    category: str
    amount: float


@dataclass
class ExpenseComment:
    """"""

    id: str
    user: str
    avatar: str
    text: str
    timestamp: str


@dataclass
class ExpenseHistory:
    """"""

    action: str
    user: str
    timestamp: str
    note: str


@dataclass
class Expense:
    """"""

    date: str
    description: str
    amount: float
    category: str
    payment_type: str
    exclude_flag: bool = False
    recurring_flag: bool = False
    has_source_file: bool = False
    location: list[str] = field(default_factory=list)

    splits: list[ExpenseSplit] = field(default_factory=list)
    comments: list[ExpenseComment] = field(default_factory=list)
    history: list[ExpenseHistory] = field(default_factory=list)
    assigned_approver_id: str = ""
    source_file: str = ""


@dataclass
class BudgetStats:
    """"""

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

    budgets: list[Budget] = [Budget(**x) for x in DATA_CONFIG.budget_allocations]
    expenses: list[Expense] = [Expense(**x) for x in list(DATA_CONFIG.get_row_iterable)]
    warning_threshold: int = 75
    critical_threshold: int = 90

    @rx.var
    def total_budget(self) -> float:
        """"""
        return sum(b.allocated_amount for b in self.budgets)

    @rx.var
    def total_spent(self) -> float:
        """"""
        return sum(e.amount for e in self.expenses if not e.exclude_flag)

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
    def budget_vs_actual_spend(self) -> list[dict[str, typing.Any]]:
        """"""

        data = []
        for budget in self.budgets:
            category_spent = sum(
                e.amount
                for e in self.expenses
                if e.category == budget.name and not e.exclude_flag
            )
            data.append(
                {
                    "name": budget.name,
                    "allocated": budget.allocated_amount,
                    "spent": category_spent,
                }
            )
        return data

    @rx.var
    def budget_health_stats(self) -> list[BudgetStats]:
        """"""

        stats = []
        for b in self.budgets:
            spent = sum(
                e.amount
                for e in self.expenses
                if e.category == b.name and not e.exclude_flag
            )
            total = b.allocated_amount
            utilization = (spent / total * 100) if total > 0 else 0.0
            color = (
                "red"
                if utilization > self.critical_threshold
                else "orange"
                if utilization > self.warning_threshold
                else "emerald"
            )

            stats.append(
                BudgetStats(
                    name=b.name,
                    type=b.type,
                    allocated_amount=total,
                    period=b.period,
                    spent=spent,
                    remaining=total - spent,
                    utilization=round(utilization, 1),
                    health_color=f"text-{color}-500",
                    health_bg=f"bg-{color}-50",
                    progress_color=f"bg-{color}-500",
                )
            )

        return stats

    @rx.event
    def open_add_budget_modal(self):
        """"""
        return rx.toast("New Budget feature coming soon!")

    @rx.event
    def open_add_expense_modal(self):
        """"""
        return rx.toast("New Expense feature coming soon!")
