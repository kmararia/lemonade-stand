"""A module to help read and write delta lakes as needed"""

import shutil
from pathlib import Path
from typing import Any

import polars as pl

from .exceptions import MissingDeltaError
from .logging import set_up_logger

LOGGER = set_up_logger(__name__)


def read_delta(table: str, search_dir: Path) -> pl.LazyFrame:
    """A function that finds the delta lake associated with the table and reads it in as a polars dataframe

    Arguments:
        table: The respective file/dataset name
        search_dir: A directory to search for the table in
    Returns:
        A polars lazyframe

    """

    parquet_path = search_dir / table
    if not parquet_path.exists():
        raise MissingDeltaError(
            f"Table or file '{table}' is missing in the following directory: \n\t{search_dir}"
        )

    # Confirm parquet file(s) are available
    if parquet_path.is_dir() and (
        len(list(parquet_path.glob("*.parquet"))) >= 1
        or len(list(parquet_path.glob("_delta_log"))) > 0
    ):
        pass
    else:
        raise FileNotFoundError(
            f"Found file/dir does not contain any readable parquet files!! \n\t{parquet_path}"
        )

    LOGGER.info("Reading deltalake: %s", parquet_path)

    return pl.scan_delta(source=parquet_path)


def write_delta(write_info_dict: dict[str, dict[str, Any]], write_dir: Path) -> Path:
    """
    A function that to write out delta lakes to a specified directory

    Arguments:
        write_info_dict: A dictionary where keys are table names and values are dictionaries containing a polars DataFrame and optional partitioning information
        write_dir: A directory path to write to
    Returns:
        A path object to the written delta lake
    """

    # Create directory if it does not exist
    write_dir.mkdir(parents=True, exist_ok=True)

    for table, data_info in write_info_dict.items():
        parquet_path = write_dir / table
        data_df = data_info["dataframe"]
        partition_by = data_info.get("partition_by", ["source_file"])

        if parquet_path.exists():
            LOGGER.warning(
                "Table '%s' already exists. Overwriting it in the following directory: \n\t%s",
                table,
                write_dir,
            )
            shutil.rmtree(parquet_path)

        if not set(partition_by).issubset(set(data_df.columns)):
            raise ValueError(
                f"Partition columns {partition_by} are not all present in the dataframe columns {data_df.columns}"
            )

        data_df.write_delta(
            target=parquet_path,
            mode=data_info.get("mode", "overwrite"),
            delta_write_options={"partition_by": partition_by},
        )

    return write_dir
