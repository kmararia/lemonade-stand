""" """

import typing
from dataclasses import dataclass

import polars as pl
import reflex as rx

from lemonade_stand.ui.states.data_state import DataState


@dataclass
class TransactionActivity:
    """"""

    date: str
    description: str
    amount: float
    payment_type: str
    health_color: str


@dataclass
class BudgetHealthStats:
    """"""

    category: str
    spent_amount: float
    allocated_amount: float
    remaining_amount: float
    utilization: float
    health_color: str
    health_bg: str
    progress_color: str


class HomeState(DataState):
    """Core state for budget and expense data."""

    warning_threshold: int = 75
    critical_threshold: int = 90

    @rx.var(cache=True)
    def recent_activity(self) -> list[TransactionActivity]:
        """"""

        return [
            TransactionActivity(**row)
            for row in (
                pl.concat(
                    [
                        self._shared_data.income,
                        self._shared_data.savings,
                        self._shared_data.expenses,
                    ]
                )
                .sort("date", descending=True)
                .select(
                    date=pl.col("date").dt.strftime("%m/%d/%Y"),
                    description=pl.col("description"),
                    amount=pl.col("amount").round(2),
                    payment_type=(
                        pl.when(
                            pl.col("payment").str.contains("(?i)card"),
                        )
                        .then(pl.lit("credit_card"))
                        .otherwise(pl.lit("badge_cent"))
                    ),
                    health_color=pl.col("payment_type").replace_strict(
                        {
                            "income": "green",
                            "savings": "blue",
                            "expenses": "yellow",
                            "unknown": "gray",
                        },
                        default="gray",
                    ),
                )
                .collect()
            ).to_dicts()
        ]

    @rx.var(cache=True)
    def home_page_data(self) -> list[dict[str, typing.Any]]:
        """"""

        return (
            self._shared_data.expenses.join(
                pl.LazyFrame(self.allocation_rows),
                on="category",
                how="left",
                coalesce=True,
            )
            .group_by(
                allocated_amount=pl.col("allocated_amount"),
                payment_type=pl.col("payment_type"),
                category=(
                    pl.when(pl.col("category").str.len_chars() <= 20)
                    .then(pl.col("category"))
                    .otherwise(pl.col("category").str.slice(0, 19) + "...")
                    .str.replace_all(r"(?i)\s+\b(AND)\b\s+", " & ")
                ),
            )
            .agg(
                spent_amount=(
                    pl.when(pl.col("exclude_flag"))
                    .then(pl.col("amount"))
                    .otherwise(0)
                    .sum()
                )
            )
            .with_columns(
                remaining_amount=(pl.col("allocated_amount") - pl.col("spent_amount")),
                utilization=(
                    pl.when(pl.col("allocated_amount") > 0)
                    .then(
                        (
                            pl.col("spent_amount") / pl.col("allocated_amount") * 100
                        ).round(1)
                    )
                    .otherwise(0.0)
                ),
            )
            .with_columns(
                color=(
                    pl.when(pl.col("utilization") > self.critical_threshold)
                    .then(pl.lit("red"))
                    .otherwise(
                        pl.when(pl.col("utilization") > self.warning_threshold)
                        .then(pl.lit("orange"))
                        .otherwise(pl.lit("emerald"))
                    )
                )
            )
            .sort("allocated_amount", descending=False)
            .collect()
        ).to_dicts()

    @rx.var
    def budget_vs_actual_spend(self) -> list[dict[str, typing.Any]]:
        """"""

        return [
            {
                "category": x["category"],
                "spent_amount": x["spent_amount"],
                "allocated_amount": x["allocated_amount"],
            }
            for x in self.home_page_data
        ]

    @rx.var
    def budget_health_stats(self) -> list[BudgetHealthStats]:
        """"""

        return [
            BudgetHealthStats(
                category=x["category"],
                spent_amount=x["spent_amount"],
                allocated_amount=x["allocated_amount"],
                remaining_amount=x["remaining_amount"],
                utilization=x["utilization"],
                health_color=f"text-{x['color']}-500",
                health_bg=f"bg-{x['color']}-50",
                progress_color=f"bg-{x['color']}-500",
            )
            for x in self.home_page_data
        ]

    @rx.event
    def open_add_budget_modal(self):
        """"""
        return rx.toast("New Budget feature coming soon!")

    @rx.event
    def open_add_expense_modal(self):
        """"""
        return rx.toast("New Expense feature coming soon!")

    @rx.event
    def open_add_budget_allocations(self):
        """"""
        return rx.toast("New Budget Allocations feature coming soon!")
