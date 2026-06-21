""""""

from dataclasses import dataclass
from dataclasses import field

import polars as pl
import reflex as rx

from lemonade_stand.ui.states.data_state import DataState

STROKE_COLORS = ["#22D3EE", "#4ADE80", "#D97706", "#ec4899", "#8b5cf6"]


@dataclass
class Income:
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
    source_file: str = ""


class IncomeState(DataState):
    """Core state for budget and income data."""

    @rx.var(cache=True)
    def income_rows(self) -> list[Income]:
        """Filter data based on the selected date range from DateState."""

        row_iterator = (
            self._shared_data.income.select(
                "date",
                "description",
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
        ).iter_rows(named=True)

        return [Income(**row) for row in row_iterator]

    @rx.var
    def spending_trends_data(self) -> list[dict]:
        """"""

        category_names = [x["name"] for x in self.income_category_list]

        return (
            self._shared_data.income.filter(
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
    def income_category_list(self) -> list[dict]:
        """"""

        row_iterator = (
            self._shared_data.income.group_by(name=pl.col("category"))
            .agg(pl.col("amount").sum())
            .sort("amount", descending=True)
            .with_row_index("index")
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

        return [
            {
                **row,
                "clean_name": row["name"].replace(" ", "_"),
                "fill": STROKE_COLORS[row["index"] % len(STROKE_COLORS)],
                "type": "monotone",
            }
            for row in row_iterator[: len(STROKE_COLORS)]
        ]

    @rx.var
    def total_earnings(self) -> float:
        """"""
        return (self._shared_data.income.select(pl.col("amount").sum()).collect()).item(
            0, 0
        )

    @rx.var
    def top_income_category(self) -> str:
        """"""
        if len(self.income_category_list) == 0:
            return "N/A"
        return self.income_category_list[0]["name"]
