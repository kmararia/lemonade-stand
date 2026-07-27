"""Module for managing user allocations."""

import json
import typing
from dataclasses import InitVar
from dataclasses import dataclass
from dataclasses import field

import polars as pl

from lemonade_stand.config.paths import AppPaths
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)
UI_DIR = AppPaths().ui_dir


@dataclass
class Allocations:
    """Class to manage allocations."""

    _transaction_df: InitVar[pl.LazyFrame]
    name: str
    as_dicts: list[dict[str, typing.Any]] = field(default_factory=list)
    as_frame: pl.LazyFrame = field(default_factory=lambda: pl.LazyFrame())
    transaction_info: dict = field(default_factory=dict)

    def __post_init__(self, _transaction_df: pl.LazyFrame):
        """Initializes the allocations data"""

        precomp_allocations = self.compute_allocations(data_df=_transaction_df)
        self.transaction_info = dict(
            precomp_allocations.select(
                "category",
                pl.struct(
                    transaction_amount="transaction_amount",
                    n_months="n_months",
                ),
            )
            .collect()
            .iter_rows()
        )

        # Search for the configuration file in the path
        config_path = UI_DIR / "allocations.json"

        if config_path.exists():
            with config_path.open("r") as file:
                config_dict = json.load(file)

                if self.name not in config_dict:
                    LOGGER.info("No allocations data found for '%s'", self.name)
                else:
                    self.as_dicts = [
                        {
                            **row,
                            **self.transaction_info.get(
                                row["category"],
                                {"n_months": 1, "transaction_amount": 0},
                            ),
                            **(
                                {}
                                if "progress" in row
                                else {
                                    "progress": (
                                        (
                                            self.transaction_info.get(
                                                row["category"], {}
                                            ).get("transaction_amount", 0)
                                            / row["allocated_amount"]
                                            * 100
                                        )
                                        if row["allocated_amount"] > 0
                                        else 0
                                    )
                                }
                            ),
                        }
                        for row in config_dict[self.name]
                    ]
                    self.as_frame = pl.LazyFrame(self.as_dicts)
                    self.save_config()

                    return

        self.as_frame = precomp_allocations
        self.as_dicts = precomp_allocations.collect().to_dicts()
        self.save_config()

    def compute_allocations(self, data_df: pl.LazyFrame) -> pl.LazyFrame:
        """"""

        new_allocations = (
            data_df.with_columns(
                n_months=pl.col("date").dt.strftime("%Y-%m").n_unique()
            )
            .select(
                category=pl.col("category"),
                n_months=pl.col("n_months"),
                transaction_amount=pl.col("amount")
                .abs()
                .sum()
                .over("category")
                .round(0),
                allocated_amount=pl.coalesce(
                    (
                        pl.col("amount").abs().mean().over("category")
                        * pl.col("n_months")
                    ),
                    pl.lit(0),
                ).round(0),
            )
            .with_columns(
                progress=pl.when(pl.col("allocated_amount") > 0)
                .then(pl.col("transaction_amount") / pl.col("allocated_amount") * 100)
                .otherwise(pl.lit(0))
            )
            .unique()
        )

        if new_allocations.first().collect().is_empty():
            return pl.LazyFrame(
                data=[],
                schema=pl.Schema(
                    {
                        "category": pl.Utf8,
                        "n_months": pl.Int64,
                        "transaction_amount": pl.Float64,
                        "allocated_amount": pl.Float64,
                        "progress": pl.Float64,
                    }
                ),
                orient="row",
            )

        return new_allocations

    def save_config(self):
        """Saves the user allocations to a json file"""

        # Setup parent directories
        config_path = UI_DIR / "allocations.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if config_path.exists():
            with config_path.open("r+") as file:
                curr_config = json.load(file)
                if self.as_dicts != curr_config.get(self.name, []):
                    curr_config[self.name] = self.as_dicts
                    file.seek(0)
                    file.truncate()
                    json.dump(curr_config, file, indent=4)
        else:
            with config_path.open("w") as file:
                json.dump({self.name: self.as_dicts}, file, indent=4)

            LOGGER.info("Allocations data saved to: \n\t%s", config_path)

    def add_allocation(self, category: str, allocated_amount: float) -> bool:
        """Adds a new allocation to the allocations data"""

        if any(x["category"] == category for x in self.as_dicts):
            return False
        else:
            self.as_dicts.append(
                {
                    "category": category,
                    "n_months": (
                        self.transaction_info.get(category, {}).get("n_months", 1)
                    ),
                    "transaction_amount": (
                        self.transaction_info.get(category, {}).get(
                            "transaction_amount", 0
                        )
                    ),
                    "allocated_amount": allocated_amount,
                    "progress": (
                        (
                            self.transaction_info.get(category, {}).get(
                                "transaction_amount", 0
                            )
                            / allocated_amount
                            * 100
                        )
                        if allocated_amount > 0
                        else 0
                    ),
                }
            )
            self.as_frame = pl.LazyFrame(self.as_dicts)
            self.save_config()

            return True
