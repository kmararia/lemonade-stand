""" """

from dataclasses import dataclass

import polars as pl
from dash import Dash

from banana_stand.dashboard.pages import add_income_layout


@dataclass
class WebApp:
    """
    A dataclass for the web applicaton
    """

    app: Dash
    income_data: pl.DataFrame

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        self.app = add_income_layout(
            data_df=self.income_data,
            app=self.app,
        )
