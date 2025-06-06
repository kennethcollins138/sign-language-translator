import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml
from pydantic import BaseModel

# --------------------------------------------------------------------------- #
# Set-up: patch the project logger **before** importing the registry
# --------------------------------------------------------------------------- #
mock_logger = MagicMock()

with patch("src.core.logging.setup_logger", return_value=mock_logger):
    from src.core.config.exception import (
        ConfigLoadError,
        ConfigPathError,
        ConfigSaveError,
    )
    from src.core.config.registry import ConfigRegistry


# --------------------------------------------------------------------------- #
# Helper Pydantic models used throughout the tests
# --------------------------------------------------------------------------- #
class TestConfig(BaseModel):
    value: str = "default"
    number: int = 123

    class Config:  # Pydantic-v1 style still works with v2 compatibility layer
        validate_assignment = True
        extra = "forbid"


class NestedTestConfig(BaseModel):
    name: str
    settings: dict
    enabled: bool = True

    class Config:
        validate_assignment = True
        extra = "forbid"


# --------------------------------------------------------------------------- #
# Config Registry Test Suite
# --------------------------------------------------------------------------- #
class TestConfigRegistry(unittest.TestCase):
    """Unit tests for ConfigRegistry"""

    # --------------------------------------------------------------------- #
    #                                set-up                                 #
    # --------------------------------------------------------------------- #
    def setUp(self) -> None:
        # Reset the singleton and internal state
        ConfigRegistry._instance = None
        ConfigRegistry._config_schemas = {}
        ConfigRegistry._config_instances = {}
        ConfigRegistry._paths = {}

        mock_logger.reset_mock()

        # Prepare temp directory & YAML files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.test_config_path = self.temp_path / "test_config.yaml"
        self.test_config_path.write_text(yaml.dump({"value": "test_value", "number": 456}))

        self.nested_config_path = self.temp_path / "nested_config.yaml"
        self.nested_config_path.write_text(
            yaml.dump(
                {
                    "name": "nested",
                    "settings": {"debug": True, "timeout": 30},
                    "enabled": False,
                }
            )
        )

        self.empty_config_path = self.temp_path / "empty.yaml"
        self.empty_config_path.write_text("")  # really empty

        # Register schemas & paths for the tests
        registry = ConfigRegistry()
        registry.register_config_schema("test", TestConfig)
        registry.register_config_schema("nested", NestedTestConfig)

        registry.register_path("test_config", self.test_config_path)
        registry.register_path("nested_config", self.nested_config_path)
        registry.register_path("empty_config", self.empty_config_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    # --------------------------------------------------------------------- #
    #                          basic behaviour                              #
    # --------------------------------------------------------------------- #
    def test_singleton_pattern(self):
        self.assertIs(ConfigRegistry(), ConfigRegistry())

    def test_initialize_paths(self):
        registry = ConfigRegistry()
        for key in ("project_root", "configs_dir", "models_dir"):
            self.assertIn(key, registry._paths)

    # --------------------------------------------------------------------- #
    #                              get / path                               #
    # --------------------------------------------------------------------- #
    def test_get_path_success(self):
        self.assertEqual(ConfigRegistry().get_path("test_config"), self.test_config_path)

    def test_get_path_failure(self):
        self.assertIsNone(ConfigRegistry().get_path("does_not_exist"))

    def test_register_path_success(self):
        registry = ConfigRegistry()
        new_path = self.temp_path / "new_path.yaml"
        self.assertTrue(registry.register_path("new_path", new_path))
        self.assertEqual(registry.get_path("new_path"), new_path)

    # --------------------------------------------------------------------- #
    #                         register schema                               #
    # --------------------------------------------------------------------- #
    def test_register_config_schema_success(self):
        registry = ConfigRegistry()

        class ExtraConfig(BaseModel):
            value: str

        self.assertTrue(registry.register_config_schema("extra", ExtraConfig))
        self.assertIs(registry._config_schemas["extra"], ExtraConfig)


    # --------------------------------------------------------------------- #
    #                          load-config                                  #
    # --------------------------------------------------------------------- #
    def test_load_config_success(self):
        cfg = ConfigRegistry().load_config("test")
        self.assertIsInstance(cfg, TestConfig)
        self.assertEqual((cfg.value, cfg.number), ("test_value", 456))

    def test_load_config_with_custom_path(self):
        custom = self.temp_path / "custom.yaml"
        custom.write_text(yaml.dump({"value": "custom_value", "number": 789}))

        cfg = ConfigRegistry().load_config("test", custom)
        self.assertEqual((cfg.value, cfg.number), ("custom_value", 789))

    def test_load_config_nonexistent_schema(self):
        self.assertIsNone(ConfigRegistry().load_config("unregistered"))

    def test_load_config_nonexistent_path(self):
        class Pathless(BaseModel):
            value: str

        registry = ConfigRegistry()
        registry.register_config_schema("pathless", Pathless)
        self.assertIsNone(registry.load_config("pathless"))

    def test_load_config_nonexistent_file(self):
        class Missing(BaseModel):
            value: str

        missing_path = self.temp_path / "missing.yaml"
        registry = ConfigRegistry()
        registry.register_path("missing_config", missing_path)
        registry.register_config_schema("missing", Missing)
        self.assertIsNone(registry.load_config("missing"))

    def test_load_config_empty_file(self):
        self.assertIsNone(ConfigRegistry().load_config("empty"))

    @patch("yaml.safe_load", side_effect=yaml.YAMLError("broken"))
    def test_load_config_yaml_error(self, _):
        self.assertIsNone(ConfigRegistry().load_config("test"))

    # --------------------------------------------------------------------- #
    #                         cached retrieval                              #
    # --------------------------------------------------------------------- #
    def test_get_config_cached(self):
        registry = ConfigRegistry()
        first = registry.load_config("test")
        second = registry.get_config("test")
        self.assertIs(first, second)

    def test_get_config_not_cached(self):
        cfg = ConfigRegistry().get_config("test")
        self.assertIsInstance(cfg, TestConfig)

    # --------------------------------------------------------------------- #
    #                    create custom (copy & patch)                       #
    # --------------------------------------------------------------------- #
    def test_create_custom_config_success(self):
        registry = ConfigRegistry()
        registry.load_config("test")
        custom = registry.create_custom_config("test", value="overridden")
        self.assertEqual((custom.value, custom.number), ("overridden", 456))

    def test_create_custom_config_multiple_overrides(self):
        registry = ConfigRegistry()
        registry.load_config("test")
        custom = registry.create_custom_config("test", value="x", number=999)
        self.assertEqual((custom.value, custom.number), ("x", 999))

    def test_create_custom_config_invalid_keys(self):
        registry = ConfigRegistry()
        registry.load_config("test")
        custom = registry.create_custom_config("test", bad="ignored")
        self.assertEqual(custom.value, "test_value")  # unchanged

    def test_create_custom_config_nonexistent_base(self):
        self.assertIsNone(ConfigRegistry().create_custom_config("ghost"))

    @patch.object(ConfigRegistry, "get_config", return_value=None)
    def test_create_custom_config_error(self, _):
        self.assertIsNone(ConfigRegistry().create_custom_config("test"))

    # --------------------------------------------------------------------- #
    #                         save custom config                            #
    # --------------------------------------------------------------------- #
    def test_save_custom_config_success(self):
        registry = ConfigRegistry()
        cfg = TestConfig(value="saved", number=42)
        target = self.temp_path / "saved.yaml"

        self.assertTrue(registry.save_custom_config(cfg, target))
        self.assertTrue(target.exists())
        self.assertEqual(yaml.safe_load(target.read_text()), {"value": "saved", "number": 42})

    def test_save_custom_config_create_directory(self):
        registry = ConfigRegistry()
        cfg = TestConfig(value="deep")
        target = self.temp_path / "deep" / "nest" / "cfg.yaml"
        self.assertTrue(registry.save_custom_config(cfg, target))
        self.assertTrue(target.exists())

    @patch("yaml.dump", side_effect=ConfigSaveError("boom"))
    def test_save_custom_config_error(self, _):
        registry = ConfigRegistry()
        cfg = TestConfig()
        target = self.temp_path / "err.yaml"
        self.assertFalse(registry.save_custom_config(cfg, target))
