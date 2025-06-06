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


class InterpolationConfig(BaseModel):
    """Configuration for image interpolation."""

    type: str = Field("linear", description="Interpolation method for resizing")


class NormalizationConfig(BaseModel):
    """Configuration for image normalization."""

    alpha: int = Field(0, description="Alpha value for normalization")
    beta: int = Field(255, description="Beta value for normalization")
    type: str = Field("norm_minmax", description="Normalization method")


class ModelInputConfig(BaseModel):
    """Configuration for model input."""

    format: str = Field("RGB", description="Model input format")
    frame_width: int = Field(640, description="Frame width")
    frame_height: int = Field(640, description="Frame height")


class FrameProcessorConfig(BaseModel):
    """Configuration for frame processing"""

    interpolation: InterpolationConfig = Field(
        default_factory=InterpolationConfig, description="Interpolation settings"
    )
    normalization: NormalizationConfig = Field(
        default_factory=NormalizationConfig, description="Normalization settings"
    )
    model_input: ModelInputConfig = Field(
        default_factory=ModelInputConfig, description="Model input settings"
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }
