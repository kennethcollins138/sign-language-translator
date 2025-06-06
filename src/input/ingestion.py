from collections.abc import Generator
from typing import Any

import cv2
import loguru
from cv2 import Mat
from numpy import ndarray
from pydantic import BaseModel

from src.core import logging


class CameraIngestion:
    """
    Camera Ingestion is a class that handles the ingestion of camera data.
    It is responsible for capturing images from a camera and returning them as an array.
    The camera will be set to the default camera (0) if no camera is specified.
    If the camera is not found, an error will be raised. (Should be handled before calling this)
    When the class is instantiated, the camera is opened.
    When the class is destroyed, the camera closes.
    TODO:
        - Frame rate skipping/throttling, need to think about how to handle this
    """

    def __init__(
        self,
        config: BaseModel,
        logger: loguru.logger = None,
    ):
        """
        Initialize the camera ingestion class. Configs taken here
        :param config: config files that can be defined/pass from the controller.
        :param logger: logger object to use for logging.
        """
        # config and logging
        self.logger = logger if logger else logging.setup_logger("camera_ingestion")
        self.config = config

        # camera setup - use default camera (0) if config is None or doesn't have camera_id
        camera_id = getattr(config, "camera_id", 0) if config else 0
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError
        self.frame_width: int = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height: int = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps: int = int(self.cap.get(cv2.CAP_PROP_FPS))

    def camera_frames(self) -> Generator[Mat | ndarray, None, Any]:
        """
        This method is called in a controller to start the camera ingestion.
        Data can be passed back to the controller as a generator.
        :return:
        """
        try:
            while self.cap.isOpened():
                ok, frame = self.cap.read()
                if not ok:
                    continue
                yield frame
        finally:
            self.cap.release()

    def stop(self):
        """
        Graceful shutdown of camera object.
        Unsupported at the moment.
        Need to look into the better dunder method of __exit__ on object destruction or similar methods.

        :return:
        """
        self.cap.release()
        cv2.destroyAllWindows()
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()
