"""
UI Components package for the sign language translator dashboard.

This package contains reusable UI components that make up the main dashboard
interface, including camera display, parameter controls, and status monitoring.
"""

from .camera_widget import CameraWidget
from .control_panel import ControlPanel
from .status_bar import StatusBar

__all__ = ["CameraWidget", "ControlPanel", "StatusBar"]