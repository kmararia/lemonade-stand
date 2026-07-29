""" """

import typing
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields

import polars as pl
import reflex as rx

from lemonade_stand.config import UserConfig
from lemonade_stand.data import UserData
from lemonade_stand.data import get_data
from lemonade_stand.data.read import Statement
from lemonade_stand.ui.utils import Allocations
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)


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


def create_empty_placeholder() -> UserData:
    """Creates an empty UserData object to serve as a placeholder when no data is available."""

    data_schema = next(
        typing.cast(typing.Any, x.default_factory)()
        for x in fields(Statement)
        if x.name == "schema"
    )

    empty_df = (
        pl.Schema(
            {
                **dict(data_schema),
                "allocated_amount": pl.Int64,
            }
        )
        .to_frame()
        .lazy()
    )

    return UserData(
        income=empty_df,
        savings=empty_df,
        expenses=empty_df,
        unknown=empty_df,
    )


class DataState(rx.State):
    """"""

    _master_data: UserData | None = None
    _shared_data: UserData | None = None
    allocations: dict[str, Allocations] = {}
    selected_year: str = ""
    selected_month: str = ""

    is_edit_modal_open: bool = False
    edit_values: dict[str, typing.Any] = {}
    allocation_updates: dict[str, tuple[str, typing.Any]] = {}

    @rx.var
    def shared_data(self) -> UserData:
        """Lazily loads the user data when accessed for the first time."""

        if self._shared_data is None:
            return create_empty_placeholder()

        return self._shared_data

    def apply_allocations(self, name: str, data_df: pl.LazyFrame) -> pl.LazyFrame:
        """Applies allocations to the given data frame."""

        self.allocations[name] = Allocations(name=name, _transaction_df=data_df)

        return data_df.join(
            self.allocations[name].as_frame,
            on="category",
            how="left",
            coalesce=True,
        ).with_columns(
            allocated_amount=pl.coalesce(
                pl.col("allocated_amount"), pl.lit(0).cast(pl.Float64)
            )
        )

    def filter_data_dates(self) -> None:
        """Filter data based on the selected date range from DateState."""

        def apply_filters(name: str, data_df: pl.LazyFrame) -> pl.LazyFrame:
            """"""
            if self.selected_month != "" and self.selected_year != "":
                return_df = data_df.filter(
                    (pl.col("date").dt.strftime("%Y") == self.selected_year)
                    & (pl.col("date").dt.strftime("%B") == self.selected_month)
                )

            elif self.selected_year != "":
                return_df = data_df.filter(
                    pl.col("date").dt.strftime("%Y") == self.selected_year
                )

            else:
                return_df = data_df

            return self.apply_allocations(name, return_df)

        # Safety fallback for if user triggers a filter before data finishes loading
        if self._master_data is None:
            self.load_shared_data()

        self._shared_data = UserData(
            income=apply_filters(
                "income", typing.cast(UserData, self._master_data).income
            ),
            savings=apply_filters(
                "savings", typing.cast(UserData, self._master_data).savings
            ),
            expenses=apply_filters(
                "expenses", typing.cast(UserData, self._master_data).expenses
            ),
            unknown=apply_filters(
                "unknown", typing.cast(UserData, self._master_data).unknown
            ),
        )

    def load_user_data(self, full_refresh: bool = False) -> None:
        """Load user data from disk or refresh from scratch."""

        if full_refresh or self._master_data is None:
            if full_refresh:
                LOGGER.info("Reloading transaction data from scratch...")
                self._master_data = get_data(config=UserConfig(), full_refresh=True)

            elif self._master_data is None:
                LOGGER.info(
                    "User session active: Fetching transaction data from disk..."
                )
                self._master_data = get_data(config=UserConfig())

            # Sync initial filtered view with our master data copy
            self._shared_data = UserData(
                income=self.apply_allocations("income", self._master_data.income),
                savings=self.apply_allocations("savings", self._master_data.savings),
                expenses=self.apply_allocations("expenses", self._master_data.expenses),
                unknown=self.apply_allocations("unknown", self._master_data.unknown),
            )

    @rx.event
    def load_shared_data(self) -> None:
        """Lazily load user-data when page is loaded."""
        self.load_user_data(full_refresh=False)

    @rx.event
    def reload_data(self) -> None:
        """Reload user-data from scratch."""
        self.load_user_data(full_refresh=True)

    @rx.event
    def purge_data(self) -> None:
        """Purge all user data and reset the state."""
        pass

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
                        self.shared_data.income,
                        self.shared_data.savings,
                        self.shared_data.expenses,
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
        """Sets the selected year and updates the filtered data."""
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
