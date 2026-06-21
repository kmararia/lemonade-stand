""" """

import typing

import polars as pl
import reflex as rx

from lemonade_stand.config import UserConfig
from lemonade_stand.data import UserData
from lemonade_stand.data import get_data
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)
USER_CONFIG = UserConfig()

# Preload the data at the module level to ensure it's available when the UI loads.
_PRELOADED_DATA: UserData = get_data(config=USER_CONFIG)


class DataState(rx.State):
    """"""

    _shared_data: UserData = _PRELOADED_DATA
    selected_year: str = ""
    selected_month: str = ""

    def filter_data_dates(self) -> None:
        """Filter data based on the selected date range from DateState."""

        def apply_filters(data_df: pl.LazyFrame) -> pl.LazyFrame:
            """"""
            if self.selected_month != "" and self.selected_year != "":
                return data_df.filter(
                    (pl.col("date").dt.strftime("%Y") == self.selected_year)
                    & (pl.col("date").dt.strftime("%B") == self.selected_month)
                )

            elif self.selected_year != "":
                return data_df.filter(
                    pl.col("date").dt.strftime("%Y") == self.selected_year
                )

            else:
                return data_df

        self._shared_data = UserData(
            expenses=apply_filters(_PRELOADED_DATA.expenses),
            income=apply_filters(_PRELOADED_DATA.income),
            savings=apply_filters(_PRELOADED_DATA.savings),
            unknown=apply_filters(_PRELOADED_DATA.unknown),
        )

    @rx.var
    def allocation_rows(self) -> list[dict[str, typing.Any]]:
        """Filter data based on the selected date range from DateState."""

        return (
            self._shared_data.expenses.select(
                "category",
                allocated_amount=(
                    pl.col("amount").abs().mean().over("category")
                    * pl.col("date").dt.strftime("%Y-%m").n_unique()
                ).round(0),
            )
            .unique()
            .collect()
        ).to_dicts()

    @rx.var
    def available_months(self) -> list[str]:
        """Dynamically generate available months based on the user's expense data."""

        return [
            "All Months",  # Represents "All Months" option
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

        return ["All Years"] + (
            (
                pl.concat(
                    [
                        self._shared_data.income,
                        self._shared_data.savings,
                        self._shared_data.expenses,
                    ]
                )
                .select(
                    year=pl.col("date").dt.strftime("%Y"),
                )
                .unique()
                .sort("year")
                .collect()
            )
            .to_series()
            .to_list()
        )

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
        self.selected_year = year if year != "All Years" else ""
        self.filter_data_dates()

    @rx.event
    def set_month(self, month: str):
        """"""
        self.selected_month = month if month != "All Months" else ""
        self.filter_data_dates()
