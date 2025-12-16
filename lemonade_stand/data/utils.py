"""
Holds dataclasses for the application statement transaction set up
"""

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import overload

import polars as pl

from lemonade_stand.config import AppDir
from lemonade_stand.config import UserConfig
from lemonade_stand.data.read import read_pdfplumber
from lemonade_stand.data.read import read_pymullm  # noqa: F401
from lemonade_stand.data.setup import clean_transactions
from lemonade_stand.data.setup import get_transactions
from lemonade_stand.data.setup import map_contributors
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import write_to_database

LOGGER = set_up_logger(Path(__file__).stem)


@dataclass
class Statement:
    """
    A dataclass for a statement file
    """

    file_path: Path
    read_func: Callable
    pages: list = field(init=False)
    transactions: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables
        """

        LOGGER.info("Setting up data structure for %s", Path(self.file_path).name)

        self.pages = self.read_func(Path(self.file_path))

        full_transactions = get_transactions(
            pdf_text="\n".join(self.pages)
        ).with_columns(pl.lit(self.file_path.name).alias("source_file"))
        self.transactions = clean_transactions(data_df=full_transactions)


@dataclass
class Transactions:
    """
    A dataclass for the available statements
    """

    statements_list: list[Statement] = field(default_factory=list)
    data: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables
        """

        LOGGER.info("Setting up data structure for development transactions")

        if len(self.statements_list) > 0:
            self.data = pl.concat(
                [x.transactions for x in self.statements_list], how="vertical"
            )

    def __iter__(self):
        """
        Iterable for the transactions dataclass
        """
        for file in self.statements_list:
            yield file.transactions

    @overload
    def add(self, file_stmt: Statement): ...

    @overload
    def add(self, file_stmt: list[Statement]): ...

    def add(self, file_stmt):
        """
        Appends file statements to the classs statment list
        """

        if isinstance(file_stmt, Statement):
            self.statements_list.append(file_stmt)
        elif isinstance(file_stmt, list) and all(
            isinstance(x, Statement) for x in file_stmt
        ):
            self.statements_list += file_stmt
        else:
            raise Exception("Cannot add item to DevTransactions statements list")

        # Stack the new list and replace data
        self.data = pl.concat(
            [x.transactions for x in self.statements_list], how="vertical"
        )


@dataclass(frozen=True)
class UserData:
    """
    Dataclass for the user statement data
    """

    config: UserConfig
    income: pl.DataFrame = field(init=False)
    savings: pl.DataFrame = field(init=False)
    expenses: pl.DataFrame = field(init=False)
    unknown: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        # Load all user transactions
        statements = [
            Statement(file_path=file, read_func=read_pdfplumber)
            for file in (self.config.statement_dir).glob("*.pdf")
        ]

        transactions = Transactions(statements_list=statements)

        # Rename fields
        transactions.data = transactions.data.rename(
            {
                "transaction_date": "date",
                "transaction_category": "category",
                "transaction_desc": "detail",
                "transaction_amount": "amount",
                "transaction_type": "type",
                "source_file": "source",
            }
        )

        # Add contributor on user request
        if self.config.add_contributor:
            transactions.data = map_contributors(data_df=transactions.data)
        else:
            transactions.data = transactions.data.with_columns(
                pl.lit(None).alias("contributor")
            )

        # Define a function to create summarized data
        def summarize(filter_logic: pl.Expr, data_df: pl.DataFrame = transactions.data):
            return (
                data_df.filter(filter_logic)
                .group_by(["date", "category", "detail", "source"])
                .agg(pl.col("amount").sum().alias("amount"))
            )

        # Create summarized datasets
        income_df = summarize(filter_logic=(pl.col("type") == "income"))
        savings_df = summarize(filter_logic=(pl.col("type") == "savings"))
        expenses_df = summarize(filter_logic=(pl.col("type") == "expenses"))
        unknown_df = summarize(
            filter_logic=(~pl.col("type").is_in(["income", "savings", "expenses"]))
        )

        # Update the object variables
        object.__setattr__(self, "income", income_df)
        object.__setattr__(self, "savings", savings_df)
        object.__setattr__(self, "expenses", expenses_df)
        object.__setattr__(self, "unknown", unknown_df)

        # Write out the tables to a database
        database_path = write_to_database(
            database_path=AppDir().database_path,
            write_info_dict={
                "income": income_df,
                "savings": savings_df,
                "expenses": expenses_df,
                "unknown": unknown_df,
            },
        )

        LOGGER.info("Written tables to database path:\n\t%s", database_path)
