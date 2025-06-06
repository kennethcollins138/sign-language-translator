"""Custom exceptions for the input module."""


class CameraError(Exception):
    """Base exception for camera-related errors."""


class CameraOpenError(CameraError):
    """Raised when the camera cannot be opened."""

    def __init__(self, camera_id: int):
        super().__init__(f"Could not open camera with ID: {camera_id}")
        self.camera_id = camera_id


class FrameReadError(CameraError):
    """Raised when a frame cannot be read from the camera."""

    def __init__(self):
        super().__init__("Failed to read frame from the camera source.")


class CameraFrameRateError(CameraError):
    """Raised when the camera frame rate is invalid."""

class CameraFrameSizeError(CameraError):
    """Raised when the camera frame size is invalid."""

#----------------------------------------------------------------------------------------------------------------------------------
# Frame Processor Exceptions
#----------------------------------------------------------------------------------------------------------------------------------

class FrameProcessorError(Exception):
    """Base exception for frame processor-related errors."""

class FrameProcessorConfigError(FrameProcessorError):
    """Raised when the frame processor configuration is invalid."""

class FrameProcessorInputError(FrameProcessorError):
    """Raised when the frame processor input is invalid."""

class FrameProcessorOutputError(FrameProcessorError):
    """Raised when the frame processor output is invalid."""

class FrameProcessorInterpolationError(FrameProcessorError):
    """Raised when the frame processor interpolation is invalid."""
