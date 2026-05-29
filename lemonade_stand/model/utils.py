""" """

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from lemonade_stand.config import AppPaths

APP_PATHS = AppPaths()


@dataclass
class ModelData:
    """
    Class to hold the training data and related methods
    """

    inference_data: pl.LazyFrame
    train_data: Path | pl.LazyFrame
    func_field_cleaner: Callable
    text_field: str = "description"
    label_field: str = "category"

    def __post_init__(self) -> None:
        """Post initialization method for the dataclass"""

        if isinstance(self.train_data, Path):
            app_csv_path = APP_PATHS.model_dir / "inputs" / self.train_data.name

            # Copy the input file to the app directory
            if not app_csv_path.exists():
                app_csv_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(self.train_data, app_csv_path)

            self.train_data = self.read_csv(app_csv_path)

        else:
            ModelData.save_csv(
                *[self.train_data],
                write_path=APP_PATHS.model_dir
                / "outputs"
                / f"train_{self.label_field}_dataframe.csv",
                write_args={"separator": ",", "include_header": True},
            )

        # Prepare the training fields
        self.train_data = self.func_field_cleaner(input_df=self.train_data)

    def read_csv(self, read_path: Path) -> None:
        """
        Reads a CSV file into a polars LazyFrame.

        Returns:
            A polars LazyFrame containing the data from the CSV file.
        """

        return pl.scan_csv(
            read_path,
            separator=",",
            has_header=True,
            infer_schema=True,
            try_parse_dates=True,
        )

    @staticmethod
    def save_csv(*dataframes, write_path: Path, write_args: dict | None = None) -> None:
        """
        Saves a dictionary of polars LazyFrames to CSV files.

        Args:
            write_args: A dictionary of arguments to pass to the sink_csv method
        """

        write_args = write_args or {
            "separator": " ",
            "quote_style": "never",
            "include_header": False,
        }

        for data_df in dataframes:
            data_df.sink_csv(
                path=write_path,
                **write_args,
            )

    @staticmethod
    def lazy_train_test_split(
        data_df: pl.LazyFrame,
        fraction: float = 0.75,
        seed: int = 69420,
    ) -> tuple[pl.LazyFrame, pl.LazyFrame]:
        """
        Splits a polars LazyFrame into a train and test set.

        Args:
            data_df: LazyFrame to split
            seed (optional): Random seed for shuffling. Defaults to 69420.
            fraction (optional): Fraction that goes to train. Defaults to 0.75.
        Returns:
            A tuple of train and test LazyFrames
        """

        data_df = (
            data_df.with_columns(pl.all().shuffle(seed=seed))
            .with_row_index()
            .with_columns(is_train=pl.col("index") < pl.col("index").max() * fraction)
        )

        return (
            data_df.filter(pl.col("is_train")).drop("is_train", "index"),  # Train
            data_df.filter(~pl.col("is_train")).drop("is_train", "index"),  # Test
        )
