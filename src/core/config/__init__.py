"""
Core configuration module for the sign language translator application.

This module provides a configuration registry for the sign language translator
application. It allows for the registration and retrieval of configuration
schemas, as well as the management of configuration parameters. It also
provides a setup_logger function for setting up the logger for the application.
"""

from .registry import ConfigRegistry

__all__ = ["ConfigRegistry"]
