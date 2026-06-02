""""""

import typing
from dataclasses import dataclass
from dataclasses import field

import polars as pl
import reflex as rx

from lemonade_stand.ui.states.data_state import DataState


@dataclass
class Expense:
    """"""

    date: str
    description: str
    amount: float
    allocated_amount: float
    category: str
    payment_type: str
    exclude_flag: bool = False
    recurring_flag: bool = False
    has_source_file: bool = False
    location: list[str] = field(default_factory=list)
    assigned_approver_id: str = ""
    source_file: str = ""


@dataclass
class TopExpense:
    """"""

    index: int
    name: str
    amount: float


class ExpenseState(DataState):
    """Core state for budget and expense data."""

    @rx.var(cache=True)
    def expense_rows(self) -> list[Expense]:
        """Filter data based on the selected date range from DateState."""

        row_iterator = typing.cast(
            pl.DataFrame,
            (
                self._shared_data.expenses.join(
                    pl.LazyFrame(self.allocation_rows),
                    on="category",
                    how="left",
                    coalesce=True,
                )
                .select(
                    "date",
                    "description",
                    "allocated_amount",
                    "amount",
                    "category",
                    "payment_type",
                    "exclude_flag",
                    "recurring_flag",
                    "source_file",
                    has_source_file=pl.col("source_file").is_not_null(),
                    location=pl.concat_list("state", "city").list.drop_nulls(),
                )
                .sort("date", "amount", descending=[True, True])
                .collect()
            ),
        ).iter_rows(named=True)

        return [Expense(**row) for row in row_iterator]

    @rx.var
    def top_spending_category_list(self) -> list[TopExpense]:
        """"""
        row_iterator = typing.cast(
            pl.DataFrame,
            (
                self._shared_data.expenses.group_by(name=pl.col("category"))
                .agg(pl.col("amount").sum())
                .sort("amount", descending=True)
                .with_row_index("index", offset=1)
                .collect()
            ),
        ).to_dicts()

        return [TopExpense(**row) for row in row_iterator][:5]

    @rx.var
    def active_budgets(self) -> int:
        """"""
        return len(
            [
                x["allocated_amount"]
                for x in self.allocation_rows
                if x["allocated_amount"] > 0
            ]
        )

    @rx.var
    def total_allocations(self) -> float:
        """"""
        return sum(x["allocated_amount"] for x in self.allocation_rows)

    @rx.var
    def total_expenses(self) -> float:
        """"""
        return typing.cast(
            pl.DataFrame,
            self._shared_data.expenses.select(pl.col("amount").sum()).collect(),
        ).item(0, 0)

    @rx.var
    def remaining_budget(self) -> float:
        """"""
        return self.total_allocations - self.total_expenses

    @rx.var
    def utilization_percentage(self) -> float:
        """"""
        if self.total_allocations == 0:
            return 0.0
        return round(self.total_expenses / self.total_allocations * 100, 1)

    @rx.var
    def top_spending_category(self) -> str:
        """"""
        if len(self.top_spending_category_list) == 0:
            return "N/A"
        return self.top_spending_category_list[0].name

    @rx.event
    def set_year(self, year: str):
        """"""
        self.selected_year = year

    @rx.event
    def set_month(self, month: str):
        """"""
        self.selected_month = month
