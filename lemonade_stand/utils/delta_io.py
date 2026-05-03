"""
A module to help read and write delta lakes as needed
"""

from pathlib import Path

import polars as pl

from lemonade_stand.config.utils import AppDir

from .exceptions import MissingDeltaError
from .logging_utils import set_up_logger

LOGGER = set_up_logger(__name__)
BASE_DATA_PATH = AppDir.database_dir


def read_delta(table_name: str, search_dir: Path = BASE_DATA_PATH) -> pl.LazyFrame:
    """
    A function that finds the delta lake associated with the table and reads it in as a polars dataframe

    Arguments:
        table_name: The respective file/dataset name
        search_dir: A directory to search for the table in
    Returns:
        A polars lazyframe
    """

    # Search for files matching the file name
    full_name_matches = list(search_dir.glob(f"{table_name}"))
    final_matches = (
        full_name_matches
        if len(full_name_matches) > 0
        else list(search_dir.glob(f"{table_name}*"))
    )

    if len(final_matches) == 0:
        raise MissingDeltaError(
            f"Table or file '{table_name}' is missing in the following directory: \n\t{search_dir}"
        )
    else:
        file_match = final_matches[0]

    # Confirm parquet file(s) are available
    if (file_match.is_dir() and (len(list(file_match.glob("*.parquet"))) >= 1)) or (
        file_match.is_file() and (file_match.suffix == ".parquet")
    ):
        pass
    else:
        raise ValueError(
            "Found file/dir does not contain any readable parquet files!! \n\t{file_match}"
        )

    # Read and return lazyframe
    LOGGER.info("Reading deltalake: %s", file_match)

    return pl.scan_delta(source=file_match)


# def write_delta(
#     data_df: pl.DataFrame, table_name: str, write_dir: Path = BASE_DATA_PATH
# ) -> Path:
#     """
#     A function that to write out delta lakes to a specified directory

#     Arguments:
#         table_name: The respective file/dataset name
#         write_dir: A directory path to write to
#     Returns:
#         A path object to the written delta lake
#     """

#     data_df: pl.DataFrame = data_df

#     data_df.write_delta()
