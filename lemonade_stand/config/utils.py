"""
Holds dataclasses for the application configuration set up
"""

import os
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

from lemonade_stand.config import metadata
from lemonade_stand.config.setup import check_version
from lemonade_stand.config.setup import get_user_configs


@dataclass
class WebConfigs:  ## NOTE: Need to give user ability to update this through web app. Save configs to app dir
    """
    A dataclass to hold default images to be display on the web application
    """

    theme: str = "dark"  ## NOTE: NEED TO ADD A LIGHT THEME
    img_home: str = "/assets/images/income2.jpg"
    img_header: str = "/assets/images/income2.jpg"

    img_income: str = "/assets/images/income2.jpg"
    img_savings: str = "/assets/images/savings2.jpg"
    img_expenses: str = "/assets/images/expenses2.jpg"


@dataclass
class UserConfig:
    """
    A dataclass for the applicaton configs
    """

    app_version: str = field(init=False)
    refresh_flag: bool = field(init=False)
    add_contributor: bool = field(init=False)
    export_data: bool = field(init=False)
    statement_dir: Path = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        dirs = AppDir()

        # Set up the configurations
        config_dict = get_user_configs(
            user_config=dirs.user_config_path, session_dir=dirs.session_dir
        )

        # Update object fields variables
        self.app_version = config_dict["app-version"]
        self.refresh_flag = bool(config_dict["refresh-flag"])
        self.add_contributor = bool(config_dict["add-contributor"])
        self.export_data = bool(config_dict["export-flag"])
        self.statement_dir = Path(config_dict["statement-directory"])

    def __str__(self):
        """
        String representation of the class
        """

        print_str = [
            (f"{x.name} ({x.type}) \n\t--> {getattr(self, x.name)}")
            for x in fields(self)
        ]
        return "\n".join(print_str)


@dataclass
class AppDir:
    """
    A dataclass for the applicaton directories
    """

    current_dir: Path = Path.cwd()
    root_dir: Path = field(init=False)
    session_dir: Path = field(init=False)
    metadata_path: Path = field(init=False)
    user_config_path: Path = field(init=False)
    database_path: Path = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        self.root_dir = self.get_app_root_dir()
        self.session_dir = self.get_os_home()

        self.metadata_path = self.root_dir / "shared" / "schema" / "metadata.json"
        self.user_config_path = self.root_dir / "shared" / "config" / "user_config.json"
        self.database_path = self.root_dir / "shared" / "user_data" / "database.duckdb"

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

        return apps_dir / "lemonade-stand"

    def get_os_home(self) -> Path:
        """
        Returns the home directory of the user's operating system
        """

        # return "~/" if os.name == "posix" else "C:\\"
        return Path.cwd()


@dataclass
class ModelConfig:
    """
    A dataclass for the applicaton configs
    """

    category: str
    refresh_flag: bool = field(init=False)
    dict_data: dict = field(
        init=False
    )  ## NOTE: MAYBE NEED TO GET RID OF DICT FOR EFFICIENCY
    dot_data: SimpleNamespace = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        dirs = AppDir()

        if self.category == "model":
            self.dict_data = metadata.MODEL_CONFIG

            self.refresh_flag = check_version(
                config_path=dirs.metadata_path,
                config_dict=metadata.MODEL_CONFIG,
            )

        # Save dict as simple-namespace
        self.dot_data = SimpleNamespace(**self.dict_data)

    def __str__(self):
        """
        String representation of the class
        """

        print_str = [f"{x.name} --> ({x.type})" for x in fields(self)]
        return "\n".join(print_str)
