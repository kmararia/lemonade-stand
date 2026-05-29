"""
Unit test session fixtures for the lemonade-stand application
"""

import pytest


@pytest.fixture(scope="session")
def tmp_home_dir(tmp_path_factory):
    """Create a base temporary directory for the session"""

    return tmp_path_factory.mktemp("tests_home")
