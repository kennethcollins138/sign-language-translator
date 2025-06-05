class ConfigError(Exception):
    """Base exception for all configuration-related errors."""


class ConfigPathError(ConfigError):
    """Exception raised for errors related to configuration paths."""


class ConfigSchemaError(ConfigError):
    """Exception raised for errors related to configuration schemas."""


class ConfigLoadError(ConfigError):
    """Exception raised for errors during configuration loading."""


class ConfigValidationError(ConfigError):
    """Exception raised for configuration validation errors."""


class ConfigSaveError(ConfigError):
    """Exception raised for errors during configuration saving."""
