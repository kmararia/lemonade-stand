"""
Scrapping transactions from pdf file texts
"""

import re
from datetime import datetime
from decimal import Decimal as PyDecimal
from pathlib import Path

import numpy as np
import polars as pl
from dateutil.parser import parse

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(Path(__file__).stem)


def get_transactions(pdf_text: str) -> pl.DataFrame:
    """
    Extracts the transaction lines from a string of text

    Returns:
        A list of transaction records
    """

    LOGGER.info("Getting year of the statement")

    # Set up the statement file year
    file_year = re.search(
        re.compile(r"([A-Za-z]{3,9})\s*(\d{2}),?\s*(\b\d{4}\b)", re.IGNORECASE),
        pdf_text,
    )

    file_year = (file_year.group(3)) if file_year else (datetime.now().year)

    # Define variables
    transaction_matches = []
    date_patterns = [
        r"""
            (?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|
            Apr(?:il)?|May|Jun(?:e)?|
            Jul(?:y)?|Aug(?:ust)?|Sept(?:ember)?|
            Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+
        """,
        r"\b\d{2,4}/",
    ]

    LOGGER.info("Scraping transaction lines")

    # Iterate through all the potentail patterns
    for pattern in date_patterns:
        transactions = re.finditer(
            re.compile(
                rf"({pattern}\d{{2}})\s+(.*?)\s+(-?\d*,?\d+\.\d{{2}})",
                re.IGNORECASE | re.VERBOSE,
            ),
            pdf_text,
        )

        transaction_matches.append([line.groups() for line in transactions])

    # Set up the final schema and data
    schema = pl.Schema(
        {
            "transaction_date": pl.Date(),
            "transaction_desc": pl.String(),
            "transaction_amount": pl.Decimal(None, 2),
        }
    )

    data = [
        (
            parse(row[0], default=datetime(int(file_year), 1, 1)).date(),
            row[1],
            PyDecimal(row[2].replace(",", "")),
        )
        for row in transaction_matches[
            np.argmax(
                [len(x) for x in transaction_matches]
            )  # Get list with most transactions captured
        ]
    ]

    # Return a polars dataframe
    return pl.DataFrame(
        data=data,
        schema=schema,
        orient="row",
    )


def clean_transactions(data_df: pl.DataFrame) -> pl.DataFrame:
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
        (
            pl.col("transaction_desc").str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1)
        ).is_null()
    )

    LOGGER.info("Adding missing fields...")

    # Set up missing columns
    clean_df = clean_df.with_columns(
        pl.lit("Category").alias("transaction_category"),
        (
            pl.when(pl.col("transaction_amount") < 0)
            .then(pl.lit("expenses"))
            .otherwise(pl.lit("income"))
        ).alias("transaction_type"),
    )

    # # Filter out unnecessary data tables
    # clean_df = save_popular_block(data_df=clean_df)

    # Return clean dataframe
    return clean_df


def map_contributors(data_df: pl.DataFrame) -> pl.DataFrame:
    """
    A function to map contributors into the data

    Arguments:
        data_df: The transactions dataframe
    """

    LOGGER.info("Adding contributors to dataset")

    # Maybe process the mapping config here??
    contributor_mappings = {
        # User : Mapping str
    }

    # Assuming we iterate through a dictionary
    contributor_expr = pl.lit(None).alias("contributors")
    for user, mapping in contributor_mappings.items():
        contributor_expr = (
            pl.when(
                pl.col("transaction_desc").str.to_lowercase() == mapping.lower()
            )  # TODO: Probably need to do some regex to check for the mapping in the description
            .then(user)
            .otherwise(contributor_expr)
        )

    return data_df.with_columns(contributor_expr)
