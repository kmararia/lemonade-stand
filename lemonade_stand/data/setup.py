"""
Scrapping transactions from pdf file texts
"""

import json
import logging
import re
from datetime import datetime
from decimal import Decimal as PyDecimal
from pathlib import Path

import numpy as np
import polars as pl
from dateutil.parser import parse

from lemonade_stand.config import AppDir
from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(name=Path(__file__).stem, level=logging.ERROR)

APP_PATHS = AppDir()
DATA_SCHEMA = pl.Schema(
    {
        "transaction_date": pl.Date(),
        "transaction_desc": pl.String(),
        "transaction_amount": pl.Decimal(None, 2),
        "transaction_category": pl.String(),
        "transaction_type": pl.String(),
        "source_file": pl.String(),
        "extract_date": pl.Datetime(),
        "exclude_flag": pl.Boolean(),
    }
)


def get_transactions(pdf_text: str) -> pl.DataFrame:
    """
    Extracts the transaction lines from a string of text

    Returns:
        A list of transaction records
    """

    LOGGER.info("Getting year of the statement")

    # Define variables
    transaction_matches = []
    file_year = None
    month_patterns = {
        "Jan/January": (
            r"(?:"
            r"Jan(?:uary)?"
            r"|Feb(?:ruary)?"
            r"|Mar(?:ch)?"
            r"|Apr(?:il)?"
            r"|May"
            r"|Jun(?:e)?"
            r"|Jul(?:y)?"
            r"|Aug(?:ust)?"
            r"|Sept(?:ember)?"
            r"|Oct(?:ober)?"
            r"|Nov(?:ember)?"
            r"|Dec(?:ember)?"
            r")"
        ),
        "01": r"\d{2}",
    }

    LOGGER.info("Scraping transaction lines")

    # Iterate through all the potentail patterns
    for date_format, pattern in month_patterns.items():
        space_patt = r"[^\S\r\n]"

        # Build the statement year pattern
        if date_format == "Jan/January":
            year_pattern = rf"((?:\d{{2}}{space_patt}+{pattern})|(?:{pattern}{space_patt}+\d{{2}}),?{space_patt}*)(\b\d{{4}}\b)"  # Matches: January 31, 2024
        else:
            year_pattern = rf"({pattern}/\d{{2}}/?)(\d{{2}}|\d{{4}})"  # Matches: 04/01/24 or 04/01/2024

        LOGGER.info("Getting year of the statement")

        # Find the statement file year
        year_search = re.search(re.compile(year_pattern, re.IGNORECASE), pdf_text)
        file_year = year_search.group(2) if year_search else file_year

        # Build the full date pattern conditionally
        if date_format == "Jan/January":
            date_pattern = rf"(?:\d{{2}}{space_patt}+{pattern})|(?:{pattern}{space_patt}+\d{{2}})"  # Matches: 31 January or January 31
        else:
            date_pattern = (
                rf"{pattern}/\d{{2}}(?:/\d{{2,4}})?"  # Matches: 01/31 or 01/31/2024
            )

        # Find matches iteratively
        LOGGER.debug(
            "Checking date-format %s using pattern: \n\t%s", date_format, date_pattern
        )

        transactions = re.finditer(
            re.compile(
                rf"({date_pattern})\s+(?:{date_pattern}\s+)?(.*?)\s+(-?\d*,?\d+\.\d{{2}})",
                re.IGNORECASE | re.VERBOSE,
            ),
            pdf_text,
        )

        transaction_matches.append([line.groups() for line in transactions])

    # Populate the file year with today's date if none
    file_year = (
        datetime.strptime(file_year, "%y" if len(file_year) == 2 else "%Y")
        if file_year
        else datetime.now()
    )

    # Set up the data rows
    data = [
        (
            parse(row[0], default=file_year).date(),
            row[1],
            PyDecimal(row[2].replace(",", "")),
            None,  # Placeholder for transaction_category
            None,  # Placeholder for transaction_type
            None,  # Placeholder for source_file
            datetime.now(),  # Placeholder for extract_date
            False,  # Placeholder for exclude_flag
        )
        for row in transaction_matches[
            np.argmax(
                [len(x) for x in transaction_matches]
            )  # Get list with most transactions captured. Doing this to make sure the optimal date-pattern was captured
        ]
    ]

    # Return a polars dataframe
    return pl.DataFrame(
        data=data,
        schema=DATA_SCHEMA,
        orient="row",
    )


def generate_categories() -> pl.Expr:
    """
    Generates a polars expression from the user category mappings

    Arguments:
        None
    Returns:
        A polars expression for the category field creation
    """

    # Define the configuration file path
    config_path = APP_PATHS.category_config_path

    # Read in the category config file if it exists
    if config_path.exists():
        with config_path.open("r") as file:
            category_mappings: dict = json.load(file)
    else:
        category_mappings: dict = {}

    # Generate category field expression
    field_expr = pl.when(pl.lit(False)).then(pl.lit(None))

    for category, substring_list in category_mappings.items():
        lowercase_substring_list = [x.lower() for x in substring_list]

        field_expr = field_expr.when(
            pl.col("transaction_desc")
            .str.to_lowercase()
            .str.contains_any(lowercase_substring_list)
        ).then(pl.lit(category))

    return field_expr


def generate_types() -> pl.Expr:
    """
    Generates a polars expression from the user type mappings

    Arguments:
        None
    Returns:
        A polars expression for the transaction-type field creation
    """

    # Define the configuration file path
    config_path = APP_PATHS.types_config_path

    # Read in the category config file if it exists
    if config_path.exists():
        with config_path.open("r") as file:
            transctn_type_mappings: dict = json.load(file)
    else:
        transctn_type_mappings: dict = {}

    # Generate category field expression
    field_expr = pl.when(pl.col("transaction_amount") < 0).then(pl.lit("income"))

    for transaction_type, category_list in transctn_type_mappings.items():
        lowercase_category_list = [x.lower() for x in category_list]

        field_expr = field_expr.when(
            pl.col("transaction_category")
            .str.to_lowercase()
            .str.contains_any(lowercase_category_list)
        ).then(pl.lit(transaction_type))

    return field_expr


def flag_exclusions() -> pl.Expr:
    """
    Filters out transactions listed in the user configuration file

    Arguments:
        data_df: A polars dadtaframe
    Returns:
        A polars dataframe without the listed records
    """

    # Define the configuration file path
    config_path = APP_PATHS.exclusions_config_path

    # Read in the category config file if it exists
    if config_path.exists():
        with config_path.open("r") as file:
            exclude_transactions: dict = json.load(file)
    else:
        exclude_transactions: dict = {"exclude": []}

    # Create the transactions filter flag
    LOGGER.info("Creating and exclusion flag...")

    exclude_list = [x.lower() for x in exclude_transactions.get("exclude", [])]
    exclude_pattern = "|".join(exclude_list)

    return (
        pl.col("transaction_desc")
        .str.to_lowercase()
        .str.count_matches(rf"{exclude_pattern}")
        > 0
    ) | (
        pl.col("transaction_desc")
        .str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1)
        .is_not_null()
    )


def clean_transactions(
    data_df: pl.DataFrame, file_name: str | None = None
) -> pl.DataFrame:
    """
    Filters out transactions that are most likely invalid
    """

    def save_popular_block(data_df: pl.DataFrame) -> pl.DataFrame:
        """ """

        LOGGER.info("Saving only the necessary transaction blocks")

        # Check to see if there are multiple data tables
        date_jump_rows = (
            data_df.with_row_index(name="index")
            .with_columns(pl.col("transaction_date").shift(-1).alias("lead_date"))
            .filter(
                pl.col("transaction_date")
                > pl.col("transaction_date").shift(-1)  # .dt.total_days()
            )
        )

        indx_list = date_jump_rows["index"].to_list()

        # Grab the block with the most rows if needed
        if len(indx_list) > 0:
            keep_index = (indx_list[-1] + 1, len(data_df))
            prev_count = keep_index[1] - keep_index[0]

            for indx, row_indx in enumerate(indx_list):
                curr_count = (
                    row_indx + 1 if indx == 0 else row_indx - indx_list[indx - 1]
                )

                if curr_count > prev_count:
                    keep_index = (indx_list[indx - 1] + 1, row_indx + 1)
                    prev_count = curr_count

            return data_df.with_row_index(name="index").filter(
                pl.col("index").is_between(*keep_index)
            )
        else:
            return data_df

    LOGGER.info("Filtering out bad transactions...")

    # Filter out transactions with dollar values in description
    clean_df = data_df.filter(
        pl.col("transaction_desc").str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1).is_null()
    )

    # Pull the category and type field expressions
    categories_expr = generate_categories()
    transaction_type_expr = generate_types()
    exclude_flag_expr = flag_exclusions()

    LOGGER.info("Adding missing fields...")

    # Populate empty columns
    clean_df = clean_df.with_columns(
        categories_expr.alias("transaction_category")
    ).with_columns(
        transaction_type_expr.alias("transaction_type"),
        exclude_flag_expr.alias("exclude_flag"),
        pl.lit(file_name).alias("source_file"),
    )

    # # Filter out unnecessary data tables
    # clean_df = save_popular_block(data_df=clean_df)

    return clean_df
