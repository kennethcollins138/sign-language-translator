from collections.abc import Generator
from typing import Any, Union

import cv2
import loguru
from cv2 import Mat
from numpy import ndarray
from pydantic import BaseModel

from src.core import logging

NDIM_CHECK = 3

class CameraIngestion(BaseModel):
    """
    Camera Ingestion is a class that handles the ingestion of camera data.
    It is responsible for capturing images from a camera and returning them as an array.
    The camera will be set to the default camera (0) if no camera is specified.
    If the camera is not found, an error will be raised. (Should be handled before calling this)
    When the class is instantiated, the camera is opened.
    When the class is destroyed, the camera closes.

    Needs:
        - Frame data, configurations, etc.

    """
    def __init__(self, camera: int = 0, logger: loguru.logger = None, target_size: tuple[int, int] = (640,640) ):
        """
        Initialize the camera ingestion class. Configs taken here
        :param camera:
        """
        super().__init__()
        # config and logging
        self.logger = logger if logger else logging.setup_logger(__name__)
        # expected output size for model
        self.target_size = target_size

        # camera setup
        self.cam = cv2.VideoCapture(camera)
        self.frame_width: int = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height: int = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps: int = int(self.cam.get(cv2.CAP_PROP_FPS))

        """
        TODO: 
            - Add more configurations need to pass next stage of output likely preprocessor
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
            # TODO: Interpolation should be testable for quality vs speed tradeoff
            # another reason for passing preprocess configs into class and passing class down to CameraIngestion
            # resize frame
            resized_frame = cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)

            # normalize pixel values
            # Check if config/model requires normalization of pixel values
            # normalized_frame = resized_frame / 255.0  # noqa: ERA001

            # check if model requires BGR or RGB, convert from BGR to RGB if necessary
            is_bgr: bool = frame.ndim == NDIM_CHECK
            if is_bgr:
                self.logger(f"Grabbed frame {frame.shape}")
            yield resized_frame

    def stop(self):
        """
        Graceful shutdown of camera object.
        Unsupported at the moment.
        Need to look into the better dunder method of __exit__ on object destruction or similar methods.

        :return:
        """


    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.release()