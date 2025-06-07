"""
Configuration module for the sign language translator application.

This module provides a configuration registry for the sign language translator
application. It allows for the registration and retrieval of configuration
schemas, as well as the management of configuration parameters.
"""

from .config.registry import ConfigRegistry
from .logging import setup_logger

__all__ = ["ConfigRegistry", "setup_logger"]
