""" """

import json
import typing
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from lemonade_stand.config import AppPaths
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)
APP_PATHS = AppPaths()


@dataclass
class DataManager:
    """ """

    name: str
    input_data: pl.LazyFrame

    @property
    def get_row_iterable(self) -> Iterable[dict[str, typing.Any]]:
        """
        Returns an iterable of rows from the input data.
        """

        return typing.cast(
            pl.DataFrame,
            (
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
            ),
        ).iter_rows(named=True)

    @property
    def get_budget_allocations(self) -> list[dict[str, typing.Any]]:
        """
        Returns the budget allocations either from a config file or by processing the input data.
        """

        config_path = APP_PATHS.config_dir / f"ui_{self.name}.json"

        # Read in the UI config file if it exists
        if config_path.exists():
            with config_path.open("r") as file:
                return json.load(file)["budget_allocations"]

        else:
            return typing.cast(
                pl.DataFrame,
                (
                    self.input_data.select(
                        name=(
                            pl.when(pl.col("category").str.len_chars() <= 20)
                            .then(pl.col("category"))
                            .otherwise(pl.col("category").str.slice(0, 19) + "...")
                            .str.replace_all(r"(?i)\s+\b(AND)\b\s+", " & ")
                        ),
                        allocated_amount=(
                            pl.col("amount").abs().mean().over("category")
                        ).round(0),
                        period=pl.lit("monthly"),
                    )
                    .unique()
                    .sort("allocated_amount", descending=True)
                    .collect()
                ),
            ).to_dicts()
