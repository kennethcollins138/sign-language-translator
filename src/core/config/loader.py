from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class ConfigLoader:
    """Loads configurations from YAML files into Pydantic models"""

    @staticmethod
    def load_config(config_path: str, config_class: type[T]) -> T:
        """
        Load a configuration from YAML file into a Pydantic model
        """
        # Load base configuration
        with Path.open(Path(config_path)) as f:
            config_dict = yaml.safe_load(f)
        # Convert to Pydantic model for validation
        return config_class(**config_dict)

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
