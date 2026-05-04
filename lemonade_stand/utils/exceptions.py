"""Set up a logger with handlers"""


class VersionMismatchError(Exception):
    """A custom exception for version mismatches"""

    def __init__(self, message):
        """Class initialization method"""
        self.message = message
        super().__init__(self.message)


class MissingDatabaseError(Exception):
    """A custom exception for missing databases"""

    def __init__(self, message):
        """Class initialization method"""
        self.message = message
        super().__init__(self.message)


class MissingDeltaError(Exception):
    """A custom exception for missing matching delta file"""

    def __init__(self, message):
        """Class initialization method"""
        self.message = message
        super().__init__(self.message)
