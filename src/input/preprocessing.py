from collections import defaultdict
from typing import Union

import cv2
import loguru
from cv2 import Mat
from numpy import ndarray
from pydantic import BaseModel

from src.core import logging


class FramePreprocessor:
    """
    FramePreprocessor is a decoupled Frame Preprocessor that processes each from
    camera ingestion before passing it to the model for inference.
    It was decoupled to have flexibility in testing new models, params, and so on.
    The method process frame will handle all config passed to it which will be called in FramePreprocessor.
    """

    def __init__(self,
                 config: BaseModel,
                 logger: loguru.logger = None,
     ):
        self.logger = logger if logger else logging.setup_logger("frame_preprocessor")
        self.config = config


    def process(self, frame: Union[Mat, ndarray]) -> None | Mat | ndarray:
        """
        process is the central hub of the class for preprocessing frames.
        """
        # interpolation and resizing
        if self.config.interpolation:
            frame = cv2.resize(
                frame,
                dsize=(self.config.model_input.frame_width, self.config.model_input.frame_height),
                interpolation=self.get_interpolation_value(self.config.interpolation.type)
           )
        # normalize frame
        if self.config.normalization:
            frame = cv2.normalize(
                frame,
                None,
                alpha=self.config.normalization.alpha,
                beta=self.config.normalization.beta,
                norm_type=self.get_normalize_value(self.config.normalization.type),
                dtype=cv2.CV_32F
            )
        # handle BGR/RGB conversion if necessary
        if self.config.model_input.format == "RGB":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    
    @staticmethod
    def get_interpolation_value(interpolation: str = "linear") -> int:
        """
        Simple static method to get the cv2 interpolation value from the string
        This is all interpolation values from cv2.
        """
        values: defaultdict[str,int] = defaultdict(lambda: cv2.INTER_LINEAR, {
            "nearest": cv2.INTER_NEAREST,
            "linear": cv2.INTER_LINEAR,
            "linear_exact": cv2.INTER_LINEAR_EXACT,
            "area": cv2.INTER_AREA,
            "cubic": cv2.INTER_CUBIC,
            "lanczos": cv2.INTER_LANCZOS4,
            "nearest_exact": cv2.INTER_NEAREST_EXACT,
            "max": cv2.INTER_MAX,
            "warp_fill_outliers": cv2.WARP_FILL_OUTLIERS,
            "warp_inverse_map": cv2.WARP_INVERSE_MAP,
        })

        return values[interpolation]

    @staticmethod
    def get_normalize_value(normalization: str = "norm_minmax"):
        """
        Simple static method to get the cv2 normalization value from the string
        This is all normalization values from cv2.
        """
        values = defaultdict(lambda: cv2.NORM_MINMAX, {
            "norm_inf": cv2.NORM_INF,
            "norm_l1": cv2.NORM_L1,
            "norm_l2": cv2.NORM_L2,
            "norm_l2sqr": cv2.NORM_L2SQR,
            "norm_hamming": cv2.NORM_HAMMING,
            "norm_hamming2": cv2.NORM_HAMMING2,
            "norm_type_mask": cv2.NORM_TYPE_MASK,
            "norm_relative": cv2.NORM_RELATIVE,
            "norm_minmax": cv2.NORM_MINMAX,
        })

        return values[normalization]