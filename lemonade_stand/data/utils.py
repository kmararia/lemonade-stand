"""Holds dataclasses for the application statement transaction set up"""

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import overload

import polars as pl

from lemonade_stand.config import AppDir
from lemonade_stand.data.read import Statement
from lemonade_stand.utils import read_delta
from lemonade_stand.utils import set_up_logger
from lemonade_stand.utils import write_delta
from lemonade_stand.utils.exceptions import DataLoadingError

LOGGER = set_up_logger(Path(__file__).stem)


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
        LOGGER.info("Loading statements from path: \n\t%s\n", str(self.statement_dir))

        # Load all user transactions
        statements_list = []
        error_list = []

        for file in Path(self.statement_dir).glob("*.pdf"):
            try:
                statements_list.append(Statement(file_path=file, engine="pymullm"))
            except DataLoadingError as e:
                error_list.append((file, str(e)))

        if len(error_list) > 0:
            LOGGER.warning(
                "The following files could not be loaded:\n\t%s",
                "\n\t".join([f"{file}: \n\t\t{error}" for file, error in error_list]),
            )

        transactions = Transactions(statements_list=statements_list)

        def summarize(filter_logic: pl.Expr, data_df: pl.DataFrame = transactions.data):
            """A function to create summarized data"""
            return (
                data_df.filter(filter_logic)
                .group_by([x for x in data_df.columns if x != "amount"])
                .agg(pl.col("amount").sum().alias("amount"))
                .select(data_df.columns)
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

        # Write out to delta lake
        write_dir = AppDir().data_dir
        write_path = write_delta(
            write_info_dict={
                "income": {"dataframe": income_df},
                "savings": {"dataframe": savings_df},
                "expenses": {"dataframe": expenses_df},
                "unknown": {"dataframe": unknown_df},
            },
            write_dir=write_dir,
        )

        LOGGER.info("Written tables to delta lake path:\n\t%s", write_path)

        # Update class attributes
        for table in ["income", "savings", "expenses", "unknown"]:
            object.__setattr__(
                self, table, read_delta(table=table, search_dir=write_dir)
            )
