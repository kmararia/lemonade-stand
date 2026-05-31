""" """

import typing
from dataclasses import dataclass
from dataclasses import field

import polars as pl
import reflex as rx

from lemonade_stand.config import UserConfig
from lemonade_stand.data import UserData
from lemonade_stand.data import get_data

USER_CONFIG = UserConfig()


@dataclass
class BudgetHealthStats:
    """"""

    category: str
    allocated_amount: float
    spent_amount: float
    remaining_amount: float
    utilization: float
    health_color: str
    health_bg: str
    progress_color: str


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
    assigned_approver_id: str = ""
    source_file: str = ""


class HomeState(rx.State):
    """Core state for budget and expense data."""

    user_data: UserData = get_data(config=USER_CONFIG)
    warning_threshold: int = 75
    critical_threshold: int = 90

    selected_year: str = ""
    selected_month: str = ""
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

    @rx.var
    def available_years(self) -> list[str]:
        """Dynamically generate available years based on the user's expense data."""

        return (
            typing.cast(
                pl.DataFrame,
                (
                    self.user_data.expenses.select(
                        year=pl.col("date").dt.strftime("%Y"),
                    )
                    .unique()
                    .sort("year")
                    .collect()
                ),
            )
            .to_series()
            .to_list()
        )

    @rx.var
    def filtered_expense_data(self) -> pl.LazyFrame:
        """Filter expenses based on the selected date range from DateState."""

        if self.selected_month != "" and self.selected_year != "":
            return self.user_data.expenses.filter(
                (pl.col("date").dt.strftime("%Y") == self.selected_year)
                & (pl.col("date").dt.strftime("%B") == self.selected_month)
            )

        elif self.selected_year != "":
            return self.user_data.expenses.filter(
                pl.col("date").dt.strftime("%Y") == self.selected_year
            )

        else:
            return self.user_data.expenses

    @rx.var
    def expenses(self) -> list[Expense]:
        """"""
        row_iterable = typing.cast(
            pl.DataFrame,
            (
                self.filtered_expense_data.select(
                    "date",
                    "description",
                    "amount",
                    "category",
                    "payment_type",
                    "exclude_flag",
                    "recurring_flag",
                    "source_file",
                    pl.col("source_file").is_not_null().alias("has_source_file"),
                    pl.concat_list("state", "city").list.drop_nulls().alias("location"),
                )
                .sort("date", "amount", descending=[True, True])
                .limit(6)
                .collect()
            ),
        ).iter_rows(named=True)

        return [Expense(**x) for x in row_iterable]

    @rx.var
    def home_page_data(self) -> pl.DataFrame:
        """"""

        return typing.cast(
            pl.DataFrame,
            (
                self.filtered_expense_data.group_by(
                    payment_type=pl.col("payment_type"),
                    category=(
                        pl.when(pl.col("category").str.len_chars() <= 20)
                        .then(pl.col("category"))
                        .otherwise(pl.col("category").str.slice(0, 19) + "...")
                        .str.replace_all(r"(?i)\s+\b(AND)\b\s+", " & ")
                    ),
                    allocated_amount=(
                        pl.col("amount").abs().mean().over("category")
                        * pl.col("date").dt.strftime("%Y-%m").n_unique()
                    ).round(0),
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
                    remaining_amount=(
                        pl.col("allocated_amount") - pl.col("spent_amount")
                    ),
                    utilization=(
                        pl.when(pl.col("allocated_amount") > 0)
                        .then(
                            (
                                pl.col("spent_amount")
                                / pl.col("allocated_amount")
                                * 100
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
            ),
        )

    @rx.var
    def total_budget(self) -> float:
        """"""
        return self.home_page_data.select(pl.col("allocated_amount").sum()).item(0, 0)

    @rx.var
    def total_spent(self) -> float:
        """"""
        return self.home_page_data.select(pl.col("spent_amount").sum()).item(0, 0)

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

        return self.home_page_data.select(
            "category", "allocated_amount", "spent_amount"
        ).to_dicts()

    @rx.var
    def budget_health_stats(self) -> list[BudgetHealthStats]:
        """"""

        return [
            BudgetHealthStats(**x)
            for x in self.home_page_data.select(
                "category",
                "allocated_amount",
                "spent_amount",
                "remaining_amount",
                "utilization",
                health_color=pl.concat_str(
                    pl.lit("text-"), pl.col("color"), pl.lit("-500")
                ),
                health_bg=pl.concat_str(pl.lit("bg-"), pl.col("color"), pl.lit("-50")),
                progress_color=pl.concat_str(
                    pl.lit("bg-"), pl.col("color"), pl.lit("-500")
                ),
            ).to_dicts()
        ]

    @rx.var
    def date_selection_text(self) -> str:
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

    @rx.event
    def open_add_budget_modal(self):
        """"""
        return rx.toast("New Budget feature coming soon!")

    @rx.event
    def open_add_expense_modal(self):
        """"""
        return rx.toast("New Expense feature coming soon!")
