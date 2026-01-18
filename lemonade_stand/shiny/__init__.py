"""
Bring up module functions to the sub-package level
"""

from .pages.expenses import expense_server
from .pages.expenses import expense_ui
from .pages.home import home_server
from .pages.home import home_ui
from .pages.income import income_server
from .pages.income import income_ui
from .pages.login import auth_server
from .pages.savings import savings_server
from .pages.savings import savings_ui
from .sidebar.exclude_transactions import exclude_server
from .sidebar.exclude_transactions import exclude_ui
from .sidebar.mappings_category import mappings_category_server
from .sidebar.mappings_category import mappings_category_ui
from .sidebar.mappings_type import mappings_type_server
from .sidebar.mappings_type import mappings_type_ui
from .sidebar.settings import settings_server
from .sidebar.settings import settings_ui
from .sidebar.user_guide import user_guide_server
from .sidebar.user_guide import user_guide_ui

__all__ = [
    "exclude_server",
    "exclude_ui",
    "expense_server",
    "expense_ui",
    "home_server",
    "home_ui",
    "income_server",
    "income_ui",
    "auth_server",
    "savings_server",
    "savings_ui",
    "settings_server",
    "settings_ui",
    "user_guide_server",
    "user_guide_ui",
    "mappings_category_server",
    "mappings_category_ui",
    "mappings_type_server",
    "mappings_type_ui",
]
