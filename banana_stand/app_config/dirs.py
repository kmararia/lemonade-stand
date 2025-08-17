"""
Holds dataclasses for the application configuration set up
"""

import os
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass
class AppDir:
    """
    A dataclass for the applicaton directories
    """

    root_dir: Path = field(init=False)
    session_dir: Path = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        self.root_dir = self.get_app_root_dir()
        self.session_dir = self.get_os_home()

    def get_app_root_dir(self) -> Path:
        """
        Returns the root working directory for the application
        """

        # Windows
        if os.name == "nt":
            apps_dir = Path(os.getenv("APPDATA", Path.home()))

        # macOS
        elif os.uname().sysname == "Darwin":
            apps_dir = Path.home() / "Library" / "Application Support"

        # Linux and others
        else:
            apps_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

        return apps_dir / "banana-stand"

    def get_os_home(self) -> Path:
        """
        Returns the home directory of the user's operating system
        """

        # return "~/" if os.name == "posix" else "C:\\"
        return Path.cwd()
