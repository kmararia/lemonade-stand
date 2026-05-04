"""A module to help read and write from a duckdb database"""

from pathlib import Path
from types import SimpleNamespace
from typing import overload

import duckdb
import polars as pl

from .exceptions import MissingDatabaseError


@overload
def read_from_database(database_path: Path, table_name: str) -> pl.DataFrame: ...


@overload
def read_from_database(
    database_path: Path, table_name: None = None
) -> SimpleNamespace: ...


def read_from_database(
    database_path: Path, table_name: str | None = None
) -> SimpleNamespace | pl.DataFrame:
    """ """

    # Raise error if the database does not exist
    if not database_path.exists():
        raise MissingDatabaseError(f"Missing database: {database_path.name}")

    # Create a DuckDB connection
    with duckdb.connect(database=str(database_path)) as con:
        # Get the all table names in the database
        table_info_df = con.execute("SELECT * FROM duckdb_tables").pl()
        available_table_list = (
            table_info_df.filter(~pl.col("temporary"))
            .get_column("table_name")
            .to_list()
        )

        if table_name is not None:
            assert table_name.lower() in available_table_list, (
                f"Error: table {table_name} does not exist in database. Please check name and retry"
            )
            return pl.read_database(query=f"SELECT * FROM {table_name}", connection=con)

        # Save dataframes to a dictionary
        data_df_dicts = {
            table: pl.read_database(query=f"SELECT * FROM {table}", connection=con)
            for table in available_table_list
        }

        return SimpleNamespace(**data_df_dicts)


def write_to_database(
    database_path: Path, write_info_dict: dict[str, pl.DataFrame]
) -> Path:
    """ """

    # Create directory if it does not exist
    database_path.parent.mkdir(exist_ok=True, parents=True)

    # Create a DuckDB connection
    with duckdb.connect(database_path) as con:
        for table_name, data_df in write_info_dict.items():
            # Register dataframe with table name and write it out
            con.register(f"tmp_{table_name}", data_df.to_arrow())
            con.execute(
                f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM tmp_{table_name}
                """
            )

        # Get the all table names in the database
        table_info_df = con.execute("SELECT * FROM duckdb_tables").pl()
        available_table_list = (
            table_info_df.filter(~pl.col("temporary"))
            .get_column("table_name")
            .to_list()
        )

        # Assert tables were written
        available_table_list = [x.lower() for x in available_table_list]
        for table_name in write_info_dict:
            assert table_name.lower() in available_table_list, (
                f"Error: table {table_name} not written out. Please retry"
            )

    return database_path
