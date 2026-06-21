""""""

from dataclasses import dataclass
from dataclasses import field

import polars as pl
import reflex as rx

from lemonade_stand.ui.states.data_state import DataState
from lemonade_stand.ui.states.home_state import TransactionActivity

STROKE_COLORS = ["#6366f1", "#f97316", "#14b8a6", "#ec4899", "#8b5cf6"]


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
class ExpenseVariance:
    """"""

    category: str
    spent_amount: float
    allocated_amount: float
    utilization: float
    remaining_amount: float
    excess_amount: float


@dataclass
class TopExpense:
    """"""

    index: int
    name: str
    clean_name: str
    percent_label: str
    amount: float
    stroke: str
    type: str


class ExpenseState(DataState):
    """Core state for budget and expense data."""

    chart_view_mode: str = "Trend"
    sort_column: str = "date"
    sort_reverse: bool = True  # True = Descending, False = Ascending

    @rx.var(cache=True)
    def expense_rows(self) -> list[Expense]:
        """Filter data based on the selected date range from DateState."""

        row_iterator = (
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
                "exclude_flag",
                "recurring_flag",
                "source_file",
                payment_type=pl.col("payment"),
                has_source_file=pl.col("source_file").is_not_null(),
                location=pl.concat_list("state", "city").list.drop_nulls(),
            )
            .sort(
                self.sort_column,
                "amount",
                descending=[
                    self.sort_reverse,
                    (self.sort_reverse if self.sort_column == "amount" else True),
                ],
            )
            .collect()
        ).iter_rows(named=True)

        return [Expense(**row) for row in row_iterator]

    @rx.var(cache=True)
    def notable_transactions(self) -> list[TransactionActivity]:
        """"""

        return [
            TransactionActivity(**row)
            for row in (
                self._shared_data.expenses.sort(
                    "amount", "date", descending=[True, True]
                )
                .select(
                    date=pl.col("date").dt.strftime("%m/%d/%Y"),
                    description=pl.col("description"),
                    amount=(pl.col("amount").round(1) * -1),
                    payment_type=(
                        pl.when(
                            pl.col("payment").str.contains("(?i)card"),
                        )
                        .then(pl.lit("credit_card"))
                        .otherwise(pl.lit("badge_cent"))
                    ),
                    health_color=(
                        pl.when(pl.col("amount") > 0)
                        .then(pl.lit("yellow"))
                        .otherwise(pl.lit("green"))
                    ),
                )
                .collect()
            ).to_dicts()
        ]

    @rx.var
    def spending_trends_data(self) -> list[dict]:
        """"""

        category_names = [x.name for x in self.top_spending_category_list]

        return (
            self._shared_data.expenses.filter(
                pl.col("category").is_in(category_names)
                & (
                    pl.col("date")
                    .dt.month_start()
                    .rank(method="dense", descending=True)
                    <= 6
                )
            )
            .group_by(
                name=pl.col("category"),
                date=pl.col("date").dt.strftime("%b %Y"),
            )
            .agg(pl.col("amount").sum())
            .sort(["date", "name"], descending=[False, True])
            .pivot(
                on="name",
                on_columns=category_names,
                index="date",
                values="amount",
                maintain_order=True,
            )
            .collect()
        ).to_dicts()

    @rx.var
    def expense_variance_stats(self) -> list[ExpenseVariance]:
        """"""

        row_iterator = (
            self._shared_data.expenses.group_by("category")
            .agg(spent_amount=pl.col("amount").sum())
            .join(
                pl.LazyFrame(self.allocation_rows),
                on="category",
                how="left",
                coalesce=True,
            )
            .select(
                "category",
                "spent_amount",
                "allocated_amount",
                remaining_amount=(pl.col("allocated_amount") - pl.col("spent_amount")),
                excess_amount=(pl.col("spent_amount") - pl.col("allocated_amount")),
                utilization=(pl.col("spent_amount") / pl.col("allocated_amount") * 100),
            )
            .sort("spent_amount", descending=True)
            .collect()
        ).to_dicts()

        return [
            ExpenseVariance(
                category=x["category"],
                spent_amount=x["spent_amount"],
                allocated_amount=x["allocated_amount"],
                remaining_amount=max(0, x["remaining_amount"]),
                excess_amount=max(0, x["excess_amount"]),
                utilization=x["utilization"],
            )
            for x in row_iterator
        ]

    @rx.var
    def expense_variance_totals(self) -> dict[str, str]:
        """"""

        totals_dict = {
            "spent_amount": sum(x.spent_amount for x in self.expense_variance_stats),
            "allocated_amount": sum(
                x.allocated_amount for x in self.expense_variance_stats
            ),
            "remaining_amount": sum(
                x.remaining_amount for x in self.expense_variance_stats
            ),
            "excess_amount": sum(x.excess_amount for x in self.expense_variance_stats),
        }

        return {f"{k}": f"{v:,.2f}" for k, v in totals_dict.items()}

    @rx.var
    def expense_distribution_data(self) -> list[dict]:
        """"""

        row_iterator = (
            self._shared_data.expenses.group_by(name=pl.col("category"))
            .agg(pl.col("amount").sum())
            .sort("amount", descending=True)
            .with_row_index("index", offset=1)
            .with_columns(
                percent_label=(
                    (pl.col("amount") / pl.col("amount").sum() * 100)
                    .round(1)
                    .cast(pl.Utf8)
                    + "%"
                )
            )
            .collect()
        ).to_dicts()

        return list(row_iterator)

    @rx.var
    def top_spending_category_list(self) -> list[TopExpense]:
        """"""

        top_len_categories = self.expense_distribution_data[: len(STROKE_COLORS)]
        return [
            TopExpense(
                **row,
                clean_name=row["name"].replace(" ", "_"),
                stroke=STROKE_COLORS[i],
                type="monotone",
            )
            for i, row in enumerate(top_len_categories)
        ]

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
        return (
            self._shared_data.expenses.select(pl.col("amount").sum()).collect()
        ).item(0, 0)

    @rx.var
    def remaining_budget(self) -> float:
        """"""
        return self.total_allocations - self.total_expenses

    @rx.var
    def remaining_budget_percentage(self) -> float:
        """"""
        if self.total_allocations == 0:
            return 0.0
        return round(self.remaining_budget / self.total_allocations * 100, 1)

    @rx.var
    def percentage_of_income_spent(self) -> float:
        """"""
        income_amount = (
            self._shared_data.income.select(pl.col("amount").sum()).collect()
        ).item(0, 0)

        if income_amount == 0:
            return 0.0
        return round(self.total_expenses / income_amount * 100, 1)

    @rx.var
    def top_spending_category(self) -> str:
        """"""
        if len(self.top_spending_category_list) == 0:
            return "N/A"
        return self.top_spending_category_list[0].name

    @rx.event
    def set_chart_view_mode(self, mode: str) -> None:
        """"""
        self.chart_view_mode = mode

    @rx.event
    def toggle_table_sort(self, sort_key: str) -> None:
        """Updates the sort memory based on what the user clicks."""

        if self.sort_column == sort_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = sort_key
            self.sort_reverse = False
