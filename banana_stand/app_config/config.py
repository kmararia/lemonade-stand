"""
Holds dataclasses for the application configuration set up
"""

from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path

from banana_stand.app_config.dirs import AppDir
from banana_stand.app_config.setup import set_up_configs


@dataclass
class AppConfig:
    """
    A dataclass for the applicaton configs
    """

    simulation: bool = field(init=False)
    statement_dir: Path = field(init=False)
    root_dir: Path = field(init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        directories = AppDir()
        user_config = directories.root_dir / "shared" / "config" / "user_config.json"

        # Set up the configurations
        config_dict = set_up_configs(
            user_config=user_config, session_dir=directories.session_dir
        )

        # Update object fields variables
        self.simulation = bool(config_dict["simulation flag"])
        self.statement_dir = Path(config_dict["statement directory"])
        self.root_dir = directories.root_dir

    def __str__(self):
        """
        String representation of the class
        """

        print_str = [
            (f"{x.name} ({x.type}) \n\t--> {getattr(self, x.name)}")
            for x in fields(self)
        ]
        return "\n".join(print_str)
