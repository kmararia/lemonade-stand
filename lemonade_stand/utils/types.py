"""
A module for custom types for the application
"""

from typing import Final


# A sentinel value - indicates a missing value in a function call
class MissingType:
    """
    A sentinel value - indicates a missing value in a function call
    """

    def __repr__(self):
        """"""
        return "<MISSING>"

    def __bool__(self):
        """"""
        return False


MISSING: Final = MissingType()
