from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, TypeVar, cast

import yaml
from pydantic import BaseModel

from src.core.config.exception import ConfigLoadError, ConfigPathError, ConfigSaveError
from src.core.logging import setup_logger

T = TypeVar("T", bound=BaseModel)


class ConfigRegistry:
    """Central registry for managing configurations and paths"""

    _instance: ClassVar[ConfigRegistry | None] = None
    _config_schemas: ClassVar[dict[str, type[BaseModel]]] = {}
    _config_instances: ClassVar[dict[str, BaseModel]] = {}
    _paths: ClassVar[dict[str, Path]] = {}
    _logger = setup_logger("config_registry")

    def __new__(cls):
        """Singleton pattern to ensure only one registry exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_paths()
            return cast("ConfigRegistry", cls._instance)
        return cast("ConfigRegistry", cls._instance)

    @classmethod
    def _initialize_paths(cls) -> None:
        """Initialize default paths"""
        try:
            project_root = Path(__file__).parent.parent.parent.parent

            # Register common paths
            cls._paths = {
                "project_root": project_root,
                "configs_dir": project_root / "configs",
                "models_dir": project_root / "models",
                "data_dir": project_root / "data",
                "output_dir": project_root / "output",
                "logs_dir": project_root / "logs",

                # Component config paths
                "camera_config": project_root / "configs" / "components" / "camera.yaml",
                "processor_config": project_root / "configs" / "components" / "processor.yaml",
            }

            # Check if model config directory exists
            models_config_dir = project_root / "configs" / "components" / "models"
            if models_config_dir.exists():
                cls._paths.update({
                    "mediapipe_config": models_config_dir / "mediapipe.yaml",
                    "yolov9_config": models_config_dir / "yolov9.yaml",
                })
                cls._logger.info(f"Initialized {len(cls._paths)} default paths")
            else:
                cls._logger.info(f"Initialized {len(cls._paths)} default paths (models config dir not found)")
        except ConfigPathError:
            cls._logger.exception("Error initializing paths")

    @classmethod
    def get_path(cls, path_name: str) -> Path | None:
        """
        Get a registered path by name

        Returns None if path is not found, with an error log
        """
        if path_name not in cls._paths:
            cls._logger.error(f"Path '{path_name}' is not registered")
            return None
        return cls._paths[path_name]

    @classmethod
    def register_path(cls, path_name: str, path: Path) -> bool:
        """
        Register a new path or update an existing one

        Returns True if successful, False otherwise
        """
        try:
            cls._paths[path_name] = path
            cls._logger.debug(f"Registered path '{path_name}': {path}")
            return True
        except ConfigSaveError:
            cls._logger.exception(f"Failed to register path '{path_name}'")
            return False

    @classmethod
    def register_config_schema(cls, config_name: str, schema_class: type[BaseModel]) -> bool:
        """
        Register a configuration schema class

        Returns True if successful, False otherwise
        """
        try:
            cls._config_schemas[config_name] = schema_class
            cls._logger.debug(f"Registered config schema '{config_name}'")
            return True
        except ConfigSaveError:
            cls._logger.exception(f"Failed to register config schema '{config_name}'")
            return False

    @classmethod
    def load_config(cls, config_name: str, custom_path: Path | None = None) -> BaseModel | None:
        """
        Load a configuration by name

        Args:
            config_name: Name of the configuration to load
            custom_path: Optional custom path to load from instead of the default

        Returns:
            Loaded and validated configuration object or None if loading fails
        """
        if config_name not in cls._config_schemas:
            cls._logger.error(f"Configuration schema '{config_name}' is not registered")
            return None
        try:
            # Determine the path to load from
            if custom_path:
                config_path = custom_path
            else:
                path_key = f"{config_name}_config"
                if path_key not in cls._paths:
                    cls._logger.error(f"No default path for '{config_name}' configuration")
                    return None
                config_path = cls._paths[path_key]

            # Check if file exists
            if not config_path.exists():
                cls._logger.error(f"Configuration file not found: {config_path}")
                return None
            # Load the configuration
            with Path(config_path).open("r") as f:
                config_dict = yaml.safe_load(f)

            if config_dict is None:
                cls._logger.error(f"Empty or invalid YAML file: {config_path}")
                return None
            # Create and validate the config instance
            schema_class = cls._config_schemas[config_name]
            config_instance = schema_class(**config_dict)

            # Cache the instance
            cls._config_instances[config_name] = config_instance

            cls._logger.debug(f"Loaded configuration '{config_name}' from {config_path}")
            return config_instance

        except (yaml.YAMLError, ConfigLoadError):
            cls._logger.exception(f"Error loading configuration '{config_name}'")
            return None

    @classmethod
    def get_config(cls, config_name: str) -> BaseModel | None:
        """
        Get a loaded configuration by name
        If not already loaded, it will load the default configuration
        """
        if config_name not in cls._config_instances:
            return cls.load_config(config_name)
        return cls._config_instances[config_name]

    @classmethod
    def create_custom_config(cls, config_name: str, **overrides: Any) -> BaseModel | None:
        """
        Create a custom configuration by overriding values in the default

        Args:
            config_name: Base configuration name
            **overrides: Key-value pairs to override in the configuration

        Returns:
            A new configuration instance with overrides applied or None if creation fails
        """
        try:
            # Get the base configuration
            base_config = cls.get_config(config_name)
            if base_config is None:
                cls._logger.error(f"Failed to get base configuration for '{config_name}'")
                return None
            # Create a dictionary from the base config
            config_dict = base_config.model_dump()

            # Apply overrides
            invalid_keys = []
            for key, value in overrides.items():
                if key in config_dict:
                    config_dict[key] = value
                else:
                    invalid_keys.append(key)

            if invalid_keys:
                cls._logger.warning(
                    f"Ignoring invalid configuration parameters for '{config_name}': {', '.join(invalid_keys)}"
                )

            # Create a new instance with overrides
            schema_class = cls._config_schemas[config_name]
            custom_config = schema_class(**config_dict)

            cls._logger.debug(f"Created custom configuration for '{config_name}' with overrides: {overrides}")
            return custom_config

        except ConfigSaveError:
            cls._logger.exception(f"Failed to create custom config for '{config_name}'")
            return None

    @classmethod
    def save_custom_config(cls, config: BaseModel, save_path: Path) -> bool:
        """
        Save a custom configuration to a file

        Args:
            config: Configuration object to save
            save_path: Path to save the configuration to

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert config to dictionary
            config_dict = config.model_dump()  # Already using model_dump which is correct for v2

            # Save to YAML file
            with Path(save_path).open("w") as f:
                yaml.dump(config_dict, f, default_flow_style=False)

            cls._logger.info(f"Saved custom configuration to {save_path}")
            return True

        except ConfigSaveError:
            cls._logger.exception(f"Failed to save configuration to {save_path}")
            return False