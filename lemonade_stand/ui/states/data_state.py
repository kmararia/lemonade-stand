""" """

import typing
from dataclasses import dataclass
from dataclasses import field

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


@dataclass
class TopCategory:
    """"""

    index: int
    name: str
    clean_name: str
    percent_label: str
    amount: float
    type: str
    fill: str = ""
    stroke: str = ""


@dataclass
class DataVariance:
    """"""

    category: str
    spent_amount: float
    allocated_amount: float
    utilization: float
    remaining_amount: float
    excess_amount: float


@dataclass
class DataRow:
    """"""

    index: str
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


class DataState(rx.State):
    """"""

    _shared_data: UserData = _PRELOADED_DATA
    selected_year: str = ""
    selected_month: str = ""

    is_edit_modal_open: bool = False
    edit_values: dict[str, typing.Any] = {}

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
            pl.concat(
                [
                    self._shared_data.income,
                    self._shared_data.savings,
                    self._shared_data.expenses,
                ]
            )
            .select(
                "payment_type",
                "category",
                allocated_amount=pl.coalesce(
                    (
                        pl.col("amount").abs().mean().over("category")
                        * pl.col("date").dt.strftime("%Y-%m").n_unique()
                    ),
                    pl.lit(0),
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

    @rx.event
    def set_is_edit_modal_open(self, is_open: bool):
        """Controls the open/close state of the edit modal."""
        self.is_edit_modal_open = is_open

    @rx.event
    def set_edit_value(self, field_key: str, new_value: typing.Any):
        """Updates a specific field in the edit modal form."""
        self.edit_values[field_key] = new_value

    @rx.event
    def open_edit_modal(self, row_data: dict):
        """Pre-fills the modal form with the exact row data and opens it."""

        self.is_edit_modal_open = True
        self.edit_values = {
            x: str(y).lower() if isinstance(y, bool) else y for x, y in row_data.items()
        }

    @rx.event
    def apply_data_edits(self):
        """Saves the user changes to the delta table and closes the modal."""
        # TODO: Add delta table update logic here
        self.is_edit_modal_open = False
