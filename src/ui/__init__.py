"""
User Interface module for the sign language translator application.

This module provides a modern PyQt6-based dashboard interface for real-time
camera feed display, parameter adjustment, and system monitoring. It integrates
seamlessly with the input processing pipeline and provides an intuitive
interface for interacting with the sign language translation system.

The module is organized into components and main dashboard classes:
- components: Reusable UI widgets for specific functionality
- dashboard: Main application window that orchestrates all components
- window: Legacy main window wrapper (for compatibility)
"""

from .dashboard import Dashboard

__all__ = ["Dashboard"]
