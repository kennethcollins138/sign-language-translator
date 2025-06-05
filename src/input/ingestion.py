from collections.abc import Generator
from typing import Any, Union

import cv2
import loguru
from cv2 import Mat
from numpy import ndarray
from pydantic import BaseModel

from src.core import logging


class CameraIngestion(BaseModel):
    """
    Camera Ingestion is a class that handles the ingestion of camera data.
    It is responsible for capturing images from a camera and returning them as an array.
    The camera will be set to the default camera (0) if no camera is specified.
    If the camera is not found, an error will be raised. (Should be handled before calling this)
    When the class is instantiated, the camera is opened.
    When the class is destroyed, the camera closes.

    Needs:
        - Output stream
        - Frame data, configurations, etc.

    """
    def __init__(self, camera: int = 0, logger: loguru.logger = None ):
        """
        Initialize the camera ingestion class. Configs taken here
        :param camera:
        """
        super().__init__()
        # config and logging
        self.logger = logger if logger else logging.setup_logger(__name__)

        # camera setup
        self.cam = cv2.VideoCapture(camera)
        self.frame_width: int = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height: int = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps: int = int(self.cam.get(cv2.CAP_PROP_FPS))


        """
        TODO: Add more configurations need to pass next stage of output likely preprocessor
            - Resolution consistency, need to think about how to handle this, ffmpeg?
            - Frame rate skipping/throttling, need to think about how to handle this
            - debate about moving this to preprocessor, or just having it here for now
            
        """
    def start(self) -> Generator[Union[Mat, ndarray], Any]:  # noqa: UP007
        """
        This method is called in a controller to start the camera ingestion.
        Data can be passed back to the controller as a generator.
        Decided to keep simple entity for controlling camera feed for the time being.
        :return:
        """
        while True:
            ret, frame = self.cam.read()
            if not ret:
                # TODO: Gracefully handle frame skipping
                self.logger.error("Failed to grab frame")
                break
            # TODO: think about having preprocessing done in controller or separation of concerns
            yield frame

    def stop(self):
        """
        Graceful shutdown of camera object.
        Unsupported at the moment.
        Need to look into the better dunder method of __exit__ on object destruction or similar methods.

        :return:
        """


    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.release()