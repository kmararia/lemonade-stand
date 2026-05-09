"""Holds dataclasses for the application statement transaction set up"""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import overload

import polars as pl

from lemonade_stand.config import AppDir
from lemonade_stand.data.read import Statement
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import write_to_database

LOGGER = set_up_logger(Path(__file__).stem)
DATABASE_PATH = AppDir().database_dir / "transactions.duckdb"


@dataclass
class Transactions:
    """A dataclass for the available statements"""

    statements_list: list[Statement] = field(default_factory=list)
    data: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """Post initialization variables"""
        LOGGER.info("Creating transactions data-class...\n")

        if len(self.statements_list) > 0:
            self.data = pl.concat(
                [x.transactions for x in self.statements_list], how="vertical"
            )
        else:
            LOGGER.error("No statements pdfs were found! Setting up empty dataset...")

            self.data = pl.DataFrame(data=[], schema=Statement.schema)

    def __iter__(self):
        """Iterable for the transactions dataclass"""
        for file in self.statements_list:
            yield file.transactions

    @overload
    def add(self, file_stmt: Statement): ...

    @overload
    def add(self, file_stmt: list[Statement]): ...

    def add(self, file_stmt):
        """Appends file statements to the classs statment list"""
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
    """Dataclass for the user statement data"""

    statement_dir: str | Path
    income: pl.DataFrame = field(init=False)
    savings: pl.DataFrame = field(init=False)
    expenses: pl.DataFrame = field(init=False)
    unknown: pl.DataFrame = field(init=False)

    def __post_init__(self):
        """Post initialization variables set up"""
        LOGGER.info("Loading statements from path: \n\t'%s'\n", str(self.statement_dir))

        # Load all user transactions
        transactions = Transactions(
            statements_list=[
                Statement(file_path=file, engine="pymullm")
                for file in Path(self.statement_dir).glob("*.pdf")
            ]
        )

        # Rename fields
        field_renames = {
            "transaction_date": "date",
            "transaction_type": "type",
            "transaction_category": "category",
            "transaction_desc": "detail",
            "transaction_amount": "amount",
            "source_file": "source",
            "extract_date": "extract_date",
            "exclude_flag": "exclude_flag",
        }

        transactions.data = transactions.data.rename(field_renames)

        # Define a function to create summarized data
        def summarize(filter_logic: pl.Expr, data_df: pl.DataFrame = transactions.data):
            keep_cols = field_renames.values()
            return (
                data_df.filter(filter_logic)
                .group_by([x for x in keep_cols if x != "amount"])
                .agg(pl.col("amount").sum().alias("amount"))
                .select(keep_cols)
            )

        # Create summarized datasets
        income_df = summarize(filter_logic=(pl.col("type") == "income"))
        savings_df = summarize(filter_logic=(pl.col("type") == "savings"))
        expenses_df = summarize(filter_logic=(pl.col("type") == "expenses"))
        unknown_df = summarize(
            filter_logic=(
                ~pl.col("type").is_in(["income", "savings", "expenses"])
                | pl.col("type").is_null()
            )
        )

        # Update the object variables
        object.__setattr__(self, "income", income_df)
        object.__setattr__(self, "savings", savings_df)
        object.__setattr__(self, "expenses", expenses_df)
        object.__setattr__(self, "unknown", unknown_df)

        # Write out the tables to a database
        write_path = write_to_database(
            database_path=DATABASE_PATH,
            write_info_dict={
                "income": income_df,
                "savings": savings_df,
                "expenses": expenses_df,
                "unknown": unknown_df,
            },
        )

        LOGGER.info("Written tables to database path:\n\t%s", write_path)
