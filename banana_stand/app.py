"""
Main application module
"""

import polars as pl
from dash import Dash

from banana_stand.app_config import AppDir
from banana_stand.app_config import UserConfig
from banana_stand.dashboard import WebApp
from banana_stand.data_prep import Statement
from banana_stand.data_prep import Transactions
from banana_stand.data_prep import read_pdfplumber

DIRECTORIES = AppDir()


def create_app():
    """
    Main application function
    """

    # Set up session configurations
    run_config = UserConfig()

    # Load all user transactions
    statements = [
        Statement(file_path=file, read_func=read_pdfplumber)
        for file in (run_config.statement_dir).glob("*.pdf")
    ]

    transactions = Transactions(statements_list=statements)

    if run_config.export_data:
        pass

    # Create summarized datasets
    income_summ_df = (
        transactions.data.with_columns(
            pl.lit("category").alias("transaction_category"),
            # pl.col("date").dt.strftime("%b %Y").alias("month_year")
        )
        .rename(
            {
                "transaction_date": "date",
                "transaction_category": "category",
                "transaction_amount": "amount",
            }
        )
        .group_by(["date", "category"])
        .agg(pl.col("amount").sum().alias("amount"))
    )

    # Set up custom web style
    style_sheets = [
        {
            "href": (
                "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap"
            ),
            "rel": "stylesheet",
        }
    ]

    # Initialize web application
    dash_app = WebApp(
        income_data=income_summ_df,
        app=Dash(name=__name__, external_stylesheets=style_sheets),
    )

    return dash_app.app
