""" """

import json
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import polars as pl

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_PATHS = AppDir()


@dataclass
class DataManager:
    """ """

    name: str
    input_data: pl.LazyFrame
    current_row: dict = field(init=False)
    current_allocation: dict = field(init=False)
    budget_allocations: list[dict] = field(init=False)

    def __post_init__(self):
        """
        A post initialization method for the UI configurations.
        """

        self.budget_allocations = self.get_budget_allocations()
        self.current_allocation = (
            self.budget_allocations[0] if self.budget_allocations else {}
        )
        self.current_row = next(
            self.get_row_iterable, dict.fromkeys(self.input_data.collect_schema(), "")
        )

    @property
    def available_categories(self) -> list[str]:
        """
        Returns a list of available categories from the input dataframe.
        """

        return (
            self.input_data.select(pl.col("category").unique().sort())
            .collect()
            .to_series()
            .to_list()
        )

    @property
    def get_row_iterable(self) -> Iterable[dict]:
        """
        Returns an iterable of rows from the input data.
        """

        return (
            self.input_data.select(
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
            .iter_rows(named=True)
        )

    def get_budget_allocations(self) -> list[dict]:
        """
        Returns the budget allocations either from a config file or by processing the input data.
        """

        config_path = APP_PATHS.config_dir / f"ui_{self.name}.json"

        # Read in the UI config file if it exists
        if config_path.exists():
            with config_path.open("r") as file:
                return json.load(file)["budget_allocations"]

        else:
            return (
                self.input_data.select(
                    name=pl.col("category"),
                    type=pl.col("payment_type"),
                    allocated_amount=(
                        pl.col("amount").abs().mean().over("category")
                    ).round(0),
                    period=pl.lit("monthly"),
                )
                .unique()
                .sort("allocated_amount", descending=True)
                .collect()
                .to_dicts()
            )
