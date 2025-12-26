"""
Bring up module functions to the sub-package level
"""

from .pages.expenses import expense_server
from .pages.expenses import expense_ui
from .pages.home import home_server
from .pages.home import home_ui
from .pages.income import income_server
from .pages.income import income_ui
from .pages.savings import savings_server
from .pages.savings import savings_ui
from .pages.settings import settings_server
from .pages.settings import settings_ui
from .pages.user_guide import user_guide_server
from .pages.user_guide import user_guide_ui

__all__ = [
    "expense_server",
    "expense_ui",
    "home_server",
    "home_ui",
    "income_server",
    "income_ui",
    "savings_server",
    "savings_ui",
    "settings_server",
    "settings_ui",
    "user_guide_server",
    "user_guide_ui",
]
