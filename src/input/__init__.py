"""
Input module for the sign language translator application.

This module provides a controller based system for ingesting
camera data and preprocessing it for the model.
"""

from .ingestion import CameraIngestion
from .preprocessing import FramePreprocessor

__all__ = ["CameraIngestion", "FramePreprocessor"]
