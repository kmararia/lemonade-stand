"""
Unit tests for config utils module.
"""

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from lemonade_stand.config.metadata import BASE_CONFIG
from lemonade_stand.config.utils import AppPaths
from lemonade_stand.config.utils import UserConfig

TEST_CWD = Path(__file__).parent


class TestAppPaths:
    """Test the AppPaths dataclass"""

    @pytest.fixture
    def paths_obj(self, monkeypatch, tmp_home_dir):
        """Intercept `Path.home` with `tmp_home_dir` and set up the AppPaths object for testing"""

        monkeypatch.setattr(Path, "home", lambda: tmp_home_dir)
        return AppPaths()

    @pytest.fixture
    def application_root_dir(self, tmp_home_dir):
        """Fixture for the expected application root directory path"""
        return tmp_home_dir / ".lemonade-stand"

    def test_class_attributes(self, paths_obj, application_root_dir):
        """Test the attributes of the AppPaths dataclass"""

        assert paths_obj.root_dir == application_root_dir
        assert paths_obj.metadata_path == application_root_dir / "metadata.json"
        assert paths_obj.config_dir == application_root_dir / "configs"
        assert paths_obj.data_dir == application_root_dir / "shared" / "data"
        assert paths_obj.model_dir == application_root_dir / "shared" / "model"

    def test_get_os_home(self, paths_obj, tmp_home_dir):
        """Test the `get_os_home` method of the AppPaths dataclass"""
        assert paths_obj.get_os_home() == tmp_home_dir

    def test_get_app_root_dir(self, paths_obj, application_root_dir):
        """Test the `get_app_root_dir` method of the AppPaths dataclass"""
        assert paths_obj.get_app_root_dir() == application_root_dir


class TestUserConfig:
    """Test the UserConfig dataclass"""

    @pytest.fixture(autouse=True)
    def config_obj(self, monkeypatch, tmp_home_dir):
        """Intercept `Path.home` with `tmp_home_dir` and set up the UserConfig object for testing"""

        monkeypatch.setattr(Path, "home", lambda: tmp_home_dir)

        AppPaths().config_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(
            (TEST_CWD / "data" / "user_config.json"),
            (AppPaths().config_dir / "user_config.json"),
        )

        return UserConfig()

    @pytest.fixture
    def test_config_path(self):
        """Fixture for the path to the test user config file"""

        return TEST_CWD / "data" / "user_config.json"

    @pytest.fixture
    def saved_config_path(self):
        """Fixture for the path to the saved user config file"""

        return AppPaths().config_dir / "user_config.json"

    def test_class_attributes(self, config_obj):
        """Test the attributes of the UserConfig dataclass"""

        assert isinstance(config_obj.data, SimpleNamespace)
        assert isinstance(config_obj.model, SimpleNamespace)
        assert isinstance(config_obj.ui, SimpleNamespace)

        assert config_obj.app_version == "0.0.0"
        assert config_obj.data.always_refresh_data is True
        assert config_obj.data.statement_dir == Path("/path/to/statement/dir")
        assert (
            config_obj.model.embeddings_url
            == "https://nlp.stanford.edu/data/wordvecs/glove.2024.dolma.300d.zip"
        )
        assert config_obj.model.training_file == Path("/path/to/training/file.csv")
        assert config_obj.ui.always_skip_login is False
        assert config_obj.ui.theme == "dark"

    def test_get_user_configs(self, config_obj, saved_config_path):
        """Test the `get_user_configs` method of the UserConfig dataclass"""

        with saved_config_path.open("r") as file:
            saved_config = json.load(file)

        pulled_config = json.loads(
            json.dumps(config_obj.get_user_configs(), default=str)
        )
        assert pulled_config == saved_config

    def test_get_user_configs_no_saved_config(self, monkeypatch, config_obj):
        """Test the `get_user_configs` method of the UserConfig dataclass when no saved config exists"""

        monkeypatch.setattr(Path, "exists", lambda _: False)

        pulled_config_dict = config_obj.get_user_configs()
        assert pulled_config_dict == BASE_CONFIG

    def test_update_attribute(self, config_obj, saved_config_path, test_config_path):
        """Test the `update_attribute` method of the UserConfig dataclass"""

        new_configs = {
            "always_refresh_data": False,
            "statement_dir": "/new/path/to/statement/dir",
            # Adding this to test for backward compatibility with config keys without underscores
            "always-skip-login": True,
        }

        config_obj.update_attribute(new_configs)

        assert config_obj.data.always_refresh_data is False
        assert config_obj.data.statement_dir == Path("/new/path/to/statement/dir")
        assert config_obj.ui.always_skip_login is True

        # Confirm that the user config file is updated with the new values
        with saved_config_path.open("r") as file:
            saved_config = json.load(file)

        with test_config_path.open("r") as file:
            test_config = json.load(file)
            test_config["data"]["always-refresh-data"] = new_configs[
                "always_refresh_data"
            ]
            test_config["data"]["statement-dir"] = new_configs["statement_dir"]
            test_config["ui"]["always-skip-login"] = new_configs["always-skip-login"]

        assert saved_config == test_config
