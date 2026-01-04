"""
Brings up module functions to the sub-package level
"""

from functools import partial

import plotly.express as px

from .credentials import LoginCredentials
from .credentials import add_user_credentials
from .credentials import validate_user_credentials
from .plot import build_chart

# Define partially initialized functions
build_bar_chart = partial(build_chart, func_plotly=px.bar)
build_line_chart = partial(build_chart, func_plotly=px.line)


__all__ = [
    "build_bar_chart",
    "build_line_chart",
    "LoginCredentials",
    "add_user_credentials",
    "validate_user_credentials",
]
