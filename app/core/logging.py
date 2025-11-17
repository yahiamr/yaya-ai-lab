"""
Logging configuration for the application.

- Exposes a configure_logging(settings) function that sets up global logging.
- Exposes a get_logger(name) helper for consistent logger creation.
"""

import logging
from logging import Logger
from typing import Optional

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """
    Configure global logging based on application settings.

    - Uses DEBUG or INFO level depending on settings.DEBUG.
    - Sets a simple log format with timestamp, level, logger name, and message.
    - Optionally tweaks uvicorn-related loggers for consistency.
    """
    # Decide the base log level from settings.DEBUG
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )

    # Optional: align uvicorn loggers with our chosen level
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)


def get_logger(name: Optional[str] = None) -> Logger:
    """
    Convenience wrapper around logging.getLogger.

    If no name is provided, returns a logger named 'app'.
    Using this helper keeps logger naming consistent across the project.
    """
    return logging.getLogger(name or "app")