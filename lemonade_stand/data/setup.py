"""
Scrapping transactions from pdf file texts
"""

import logging
import re
from datetime import datetime
from decimal import Decimal as PyDecimal
from pathlib import Path

import numpy as np
import polars as pl
from dateutil.parser import parse

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(name=Path(__file__).stem, level=logging.ERROR)
DATA_SCHEMA = pl.Schema(
    {
        "transaction_date": pl.Date(),
        "transaction_desc": pl.String(),
        "transaction_amount": pl.Decimal(None, 2),
        "transaction_category": pl.String(),
        "transaction_type": pl.String(),
        "source_file": pl.String(),
        "extract_date": pl.Datetime(),
    }
)


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
        # Build the full date pattern conditionally
        if date_format == "Jan/January":
            date_pattern = rf"(?:\d{{2}}\s+{pattern})|(?:{pattern}\s+\d{{2}})"
        else:
            date_pattern = rf"{pattern}/\d{{2}}(?:/\d{{2,4}})?"

        # Find matches iteratively
        LOGGER.debug(
            "Checking date-format %s using pattern: \n\t%s", date_format, date_pattern
        )

        transactions = re.finditer(
            re.compile(
                rf"({date_pattern})\s+(.*?)\s+(-?\d*,?\d+\.\d{{2}})",
                re.IGNORECASE | re.VERBOSE,
            ),
            pdf_text,
        )

        transaction_matches.append([line.groups() for line in transactions])

    # Set up the data rows
    data = [
        (
            parse(row[0], default=datetime(int(file_year), 1, 1)).date(),
            row[1],
            PyDecimal(row[2].replace(",", "")),
            None,  # Placeholder for transaction_category
            None,  # Placeholder for transaction_type
            None,  # Placeholder for source_file
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        (
            pl.col("transaction_desc").str.extract(r"(\b-?\d*,?\d+\.\d{2}\b)", 1)
        ).is_null()
    )

    LOGGER.info("Adding missing fields...")

    # Set up empty columns
    clean_df = clean_df.with_columns(
        pl.lit(file_name).alias("source_file"),
        pl.lit("Category").alias("transaction_category"),
        (
            pl.when(pl.col("transaction_amount") < 0)
            .then(pl.lit("expenses"))
            .otherwise(pl.lit("income"))
        ).alias("transaction_type"),
    )

    # # Filter out unnecessary data tables
    # clean_df = save_popular_block(data_df=clean_df)

    return clean_df
