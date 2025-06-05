import sys
from pathlib import Path

from loguru import logger


def setup_logger(
    name: str = "",
    log_dir: Path = Path("logs"),
    console_level: str = "INFO",
    file_level: str = "DEBUG",
) -> logger.__class__:
    log_dir.mkdir(exist_ok=True)

    instance = logger.bind(name=name)
    instance.remove()

    # Console output for development
    instance.add(
        sys.stderr,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level=console_level,
        filter=lambda record: record["level"].name >= console_level,
    )

    # Main log file
    instance.add(
        log_dir / f"{name}_main.log" if name else log_dir / "main.log",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=file_level,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    # Performance metrics log
    instance.add(
        log_dir / "performance.log",
        rotation="50 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        filter=lambda record: "performance" in record["extra"],
        level="DEBUG",
        enqueue=True,
    )

    # Model inference log
    instance.add(
        log_dir / "model.log",
        rotation="100 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        filter=lambda record: "model" in record["extra"],
        level="DEBUG",
        enqueue=True,
    )

    # Critical errors
    instance.add(
        log_dir / "errors.log",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        level="ERROR",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    return instance
