""" """

import typing
from collections.abc import Callable
from pathlib import Path

import polars as pl

import lemonade_stand.load_data.clean
from lemonade_stand.config import AppPaths
from lemonade_stand.config import UserConfig
from lemonade_stand.utils import read_delta
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import write_delta

from .predict import predict_cosine_similarity
from .utils import ModelData
from .vectorize import vectorize_tfidf

LOGGER = set_up_logger(Path(__file__).stem)
MODEL_DATA_SCHEMA = pl.Schema(
    {
        "index": pl.Int32(),
        "date": pl.Date(),
        "category": pl.String(),
        "amount": pl.Float64(),
        "payment": pl.String(),
        "detail": pl.String(),
        "description": pl.String(),
        "merchant": pl.String(),
        "state": pl.String(),
        "city": pl.String(),
        "payment_type": pl.String(),
        "recurring_flag": pl.Boolean(),
        "exclude_flag": pl.Boolean(),
        "source_file": pl.String(),
        "extract_date": pl.Datetime(time_unit="us", time_zone=None),
    }
)


def assign_buckets(config: UserConfig, input_data: pl.LazyFrame) -> ModelData:
    """
    Finds the category and type of the transaction by using the description field.

    Returns:
        A polars LazyFrame with the category and type of the transaction
    """

    model_data = ModelData(
        inference_data=input_data,
        train_data=config.model.training_file,
        func_field_cleaner=lemonade_stand.load_data.clean.add_description,
    )

    predicted_df = predict_cosine_similarity(
        func_vectorize=vectorize_tfidf,
        data_model=model_data,
    ).rename({"predicted": "category"})

    model_data.inference_data = predicted_df.with_columns(
        payment_type=pl.col("category").replace_strict(
            {
                x: str(y[0]).lower()
                for x, y in (
                    typing.cast(pl.LazyFrame, model_data.train_data)
                    .select("category", "payment_type")
                    .collect()
                    .rows_by_key(
                        key="category",
                        unique=True,
                    )
                    .items()
                )
                if x is not None and y[0] is not None
            },
            default="unknown",
        )
    )

    return model_data


def run_model_pipeline(config: UserConfig, input_data: pl.LazyFrame) -> dict:
    """
    Runs the full model pipeline, including assigning buckets and writing the results to delta lake.

    Returns:
        A dictionary containing the split tables as polars DataFrames.
    """

    model_data = assign_buckets(config=config, input_data=input_data)

    # Break down transactions into individual table types
    tables = ["income", "savings", "expenses", "unknown"]
    table_dict = {
        table: {
            "dataframe": (
                model_data.inference_data.filter(pl.col("payment_type") == table)
                .with_columns(index=pl.int_range(pl.len(), dtype=pl.UInt32))
                .select(list(MODEL_DATA_SCHEMA))
            ),
        }
        for table in tables
    }

    # Write out to delta lake
    write_path = write_delta(
        write_info_dict=table_dict,
        write_dir=AppPaths().data_dir / "03_gold",
    )

    # Return the fully formed object
    LOGGER.info("Written split categories to delta lake path:\t-> %s", write_path)

    return {table: read_delta(table=table, search_dir=write_path) for table in tables}


# Expose only the necessary functions for use
__all__ = ["MODEL_DATA_SCHEMA", "assign_buckets", "run_model_pipeline"]
