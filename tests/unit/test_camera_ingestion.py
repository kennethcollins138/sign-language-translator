import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml
from pydantic import BaseModel

from src.core.config import registry

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
# Helper Pydantic models
# --------------------------------------------------------------------------- #
class TestConfig(BaseModel):
    camera_id: int = 0
    target_size: tuple[int, int] = (640, 640)
    fps_limit: int = 30

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }

class TestCameraIngestion(unittest.TestCase):
    """Unit tests for CameraIngestion"""

    # --------------------------------------------------------------------- #
    #                                set-up                                 #
    # --------------------------------------------------------------------- #
    def setUp(self) -> None:
        mock_logger.reset_mock()

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.test_config_path = self.temp_path / "test_config.yaml"
        self.test_config_path.write_text(yaml.dump({"camera_id": 0, "target_size": [640, 480], "fps_limit": 30}))
        ConfigRegistry.register_config_schema("test", TestConfig)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()