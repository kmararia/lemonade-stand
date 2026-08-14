""" """

import typing
from dataclasses import dataclass
from dataclasses import field

import polars as pl
import reflex as rx

from lemonade_stand.config import AccountConfig
from lemonade_stand.config import AppPaths
from lemonade_stand.config import UserConfig
from lemonade_stand.load_data import run_import_pipeline
from lemonade_stand.load_data import run_staging_pipeline
from lemonade_stand.model import MODEL_DATA_SCHEMA
from lemonade_stand.model import run_model_pipeline
from lemonade_stand.ui.utils import Allocations
from lemonade_stand.utils import read_delta
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils.exceptions import MissingDeltaError

LOGGER = set_up_logger(__name__)


@dataclass(frozen=True)
class UserData:
    """Dataclass for the user statement data"""

    income: pl.LazyFrame
    savings: pl.LazyFrame
    expenses: pl.LazyFrame
    unknown: pl.LazyFrame


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

    empty_df = (
        pl.Schema(
            {
                **dict(MODEL_DATA_SCHEMA),
                "allocated_amount": pl.Int64(),
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

    # Data loading vars
    is_processing: bool = False
    progress_speed: str = "1s"
    progress: int = 0
    step_text: str = ""

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

    def filter_data_dates(self) -> typing.Generator:
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
            yield from self.load_shared_data()

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
        yield

    def load_user_data(self, full_refresh: bool = False) -> typing.Generator:
        """Load user data from disk or refresh from scratch."""

        data_path = AppPaths().data_dir / "03_gold"
        config = UserConfig()

        def process_data_from_start(
            config: UserConfig,
        ) -> typing.Generator[None, None, UserData]:
            """Processes data from scratch and returns a UserData object."""

            LOGGER.info("Processing data from start...")

            self.is_processing = True
            self.progress = 10
            self.progress_speed = "1s"
            self.step_text = "Initializing pipeline..."
            yield

            self.progress = 35
            self.progress_speed = "10s"
            self.step_text = "Loading statement data..."
            yield
            transactions = run_import_pipeline(user_config=config)

            self.progress = 65
            self.step_text = "Processing the data..."
            yield
            staging_df = run_staging_pipeline(input_df=transactions.data)

            self.progress = 95
            self.progress_speed = "10s"
            self.step_text = "Running transaction model..."
            yield
            model_dict = run_model_pipeline(config=config, input_data=staging_df)

            self.progress = 100
            self.progress_speed = "1s"
            self.is_processing = False
            yield

            # Return the fully formed object
            return UserData(**model_dict)

        if full_refresh or self._master_data is None:
            if bool(config.data.always_refresh_data) or full_refresh:
                LOGGER.info("Reloading transaction data from scratch...")
                self._master_data = yield from process_data_from_start(config=config)

            elif self._master_data is None:
                LOGGER.info(
                    "User session active: Fetching transaction data from disk..."
                )

                try:
                    read_dir = data_path
                    self._master_data = UserData(
                        income=read_delta(table="income", search_dir=read_dir),
                        savings=read_delta(table="savings", search_dir=read_dir),
                        expenses=read_delta(table="expenses", search_dir=read_dir),
                        unknown=read_delta(table="unknown", search_dir=read_dir),
                    )
                except MissingDeltaError as e:
                    LOGGER.warning(
                        "An error occurred while reading pre-processed tables: %s. Processing data from start.",
                        e,
                    )
                    self._master_data = yield from process_data_from_start(
                        config=config
                    )

            # Sync initial filtered view with our master data copy
            max_date_df = (
                pl.concat(
                    [
                        self._master_data.income,
                        self._master_data.savings,
                        self._master_data.expenses,
                    ]
                )
                .select(pl.col("date").max().alias("max_date"))
                .collect()
            )

            if max_date_df.shape[0] > 0:
                max_date = max_date_df.item(0, 0)
                self.selected_year = max_date.strftime("%Y")
                self.selected_month = max_date.strftime("%B")

            yield from self.filter_data_dates()

    @rx.event()
    def load_user_data_background(self) -> typing.Generator:
        """Background task to load user data without blocking the UI."""
        config = AccountConfig()
        if config.always_skip_login and self._master_data is None:
            yield from self.load_user_data(full_refresh=False)
        else:
            yield

    @rx.event
    def load_shared_data(self) -> typing.Generator:
        """Lazily load user-data when page is loaded."""
        yield from self.load_user_data(full_refresh=False)

    @rx.event
    def reload_data(self) -> typing.Generator:
        """Reload user-data from scratch."""
        yield from self.load_user_data(full_refresh=True)

    @rx.event
    def purge_data(self) -> None:
        """Purge all user data and reset the state."""
        pass

    @rx.var
    def available_years(self) -> dict[str, list[str]]:
        """Dynamically generate available years based on the user's expense data."""

        # Safety fallback for if the data has not finished loading
        years_dto = self.shared_data if self._master_data is None else self._master_data

        years_info = (
            pl.concat(
                [
                    years_dto.income,
                    years_dto.savings,
                    years_dto.expenses,
                ]
            )
            .sort("date")
            .group_by(year=pl.col("date").dt.strftime("%Y"), maintain_order=True)
            .agg(months=pl.col("date").dt.strftime("%B").unique())
            .collect()
        ).to_dicts()

        return {**{"All Years": []}, **{x["year"]: x["months"] for x in years_info}}

    @rx.var
    def available_months(self) -> list[tuple[str, bool]]:
        """Dynamically generate available months based on the user's expense data."""

        all_months = [
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

        current_months = self.available_years.get(self.selected_year, all_months)
        return [
            ("All Months", False),
            *[(month, month not in current_months) for month in all_months],
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
    def set_year(self, year: str) -> typing.Generator:
        """Sets the selected year and updates the filtered data."""
        self.selected_year = year if year != "All Years" else ""
        yield from self.filter_data_dates()

    @rx.event
    def set_month(self, month: str) -> typing.Generator:
        """Sets the selected month and updates the filtered data."""
        self.selected_month = month if month != "All Months" else ""
        yield from self.filter_data_dates()
        yield

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
