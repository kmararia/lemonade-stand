"""Holds dataclasses for the application configuration set up"""

from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path

from lemonade_stand.utils import set_up_logger

LOGGER = set_up_logger(__name__)


@dataclass
class AppPaths:
    """A dataclass for the applicaton directories"""

    root_dir: Path = field(init=False)
    config_dir: Path = field(init=False)
    data_dir: Path = field(init=False)
    model_dir: Path = field(init=False)
    metadata_path: Path = field(init=False)

    def __post_init__(self):
        """Post initialization variables set up"""

        self.root_dir = self.get_app_root_dir()
        self.metadata_path = self.root_dir / "metadata.json"
        self.config_dir = self.root_dir / "configs"
        self.data_dir = self.root_dir / "shared" / "data"
        self.model_dir = self.root_dir / "shared" / "model"

    def __str__(self):
        """String representation of the class"""
        print_str = [f"{x.name}: \n\t--> {getattr(self, x.name)}" for x in fields(self)]

        return "\n".join(print_str)

    def get_os_home(self) -> Path:
        """Returns the home directory of the user's operating system"""
        return Path.home()

    def get_app_root_dir(self) -> Path:
        """Returns the root working directory for the application"""
        return self.get_os_home() / ".lemonade-stand"
