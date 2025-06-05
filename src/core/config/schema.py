from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    """Configuration for camera ingestion"""

    camera_id: int = Field(0, description="Camera device ID")
    target_size: tuple[int, int] = Field((640, 640), description="Target frame size")
    fps_limit: int = Field(30, description="Maximum frames per second")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class FrameProcessorConfig(BaseModel):
    """Configuration for frame processing"""

    interpolation: str = Field(
        "linear", description="Interpolation method for resizing"
    )
    normalize_alpha: int = Field(0, description="Alpha value for normalization")
    normalize_beta: int = Field(255, description="Beta value for normalization")
    normalize: str = Field("norm_minmax", description="Normalization method")
    model_input_format: str = Field("RGB", description="Model input format")
    frame_width: int = Field(640, description="Frame width")
    frame_height: int = Field(640, description="Frame height")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class ModelConfig(BaseModel):
    """Base configuration for ML models"""

    # ...model-specific configurations
