from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    """Configuration for camera ingestion"""
    camera_id: int = Field(0, description="Camera device ID")
    target_size: tuple[int, int] = Field((640, 640), description="Target frame size")
    fps_limit: int = Field(30, description="Maximum frames per second")
    interpolation: str = Field("linear", description="Interpolation method for resizing")

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }

class FrameProcessorConfig(BaseModel):
    """Configuration for frame processing"""
    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }


class ModelConfig(BaseModel):
    """Base configuration for ML models"""
    # ...model-specific configurations
