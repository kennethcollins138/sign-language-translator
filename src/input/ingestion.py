import time
from collections.abc import Generator

import cv2
import loguru
from cv2 import Mat
from numpy import ndarray
from pydantic import BaseModel

from src.core import logging
from src.input.exceptions import CameraOpenError, FrameReadError


class CameraIngestion:
    """
    Handles the ingestion of video frames from a specified camera source.

    This class is responsible for initializing and managing the connection to the
    camera, capturing frames with optional frame rate throttling, and ensuring
    resources are properly released. It can be used as a context manager.
    """

    def __init__(
        self,
        config: BaseModel,
        logger: loguru.logger = None,
        max_read_retries: int = 3,
    ):
        """
        Initializes the CameraIngestion instance.

        Args:
            config: A Pydantic model containing camera configuration,
                    including `camera_id` and `fps_limit`.
            logger: An optional logger instance. If not provided, a new one will be set up.
            max_read_retries: The maximum number of consecutive times to retry reading a frame.
        
        Raises:
            CameraOpenError: If the camera specified by `camera_id` cannot be opened.
        """
        # config and logging
        self.logger = logger if logger else logging.setup_logger("camera_ingestion")
        self.config = config
        self.max_read_retries = max_read_retries

        # camera setup - use default camera (0) if config is None or doesn't have camera_id
        camera_id = getattr(config, "camera_id", 0)
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise CameraOpenError(camera_id)

        self.frame_width: int = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height: int = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps: int = int(self.cap.get(cv2.CAP_PROP_FPS))

    def camera_frames(self) -> Generator[Mat | ndarray, None, None]:
        """
        A generator that yields frames from the camera.

        This method continuously captures frames from the camera. It includes a retry
        mechanism for transient read errors and can throttle the frame rate to a
        specified limit in the configuration.

        Yields:
            A frame from the camera as a numpy array.

        Raises:
            FrameReadError: If the camera fails to read a frame after the maximum number of retries.
        """
        read_retries = 0
        last_frame_time = 0
        min_frame_interval = 1.0 / self.config.fps_limit if self.config.fps_limit > 0 else 0

        try:
            while self.cap.isOpened():
                
                # Frame rate throttling
                current_time = time.time()
                if (current_time - last_frame_time) < min_frame_interval:
                    time.sleep(min_frame_interval - (current_time - last_frame_time))
                last_frame_time = time.time()

                ok, frame = self.cap.read()
                if not ok:
                    if read_retries < self.max_read_retries:
                        read_retries += 1
                        self.logger.warning(
                            f"Failed to read frame, retry {read_retries}/{self.max_read_retries}"
                        )
                        continue
                    raise FrameReadError
                
                read_retries = 0 # Reset on successful read
                yield frame
        finally:
            self.cap.release()

    def stop(self):
        """
        Releases the camera capture and closes any associated windows.

        This method provides a way to gracefully shut down the camera object.
        It is also called automatically when the object is used as a context
        manager.
        """
        self.cap.release()
        cv2.destroyAllWindows()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()
