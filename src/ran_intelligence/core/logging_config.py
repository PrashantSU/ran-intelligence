"""Application-wide logging configuration."""

import sys

from loguru import logger

from ran_intelligence.core.config import get_settings


def configure_logging() -> None:
    """Configure application logging."""

    settings = get_settings()

    # Remove Loguru's default handler to avoid duplicate messages.
    logger.remove()

    # Console logging.
    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - <level>{message}</level>"
        ),
        colorize=True,
        backtrace=False,
        diagnose=False,
    )


def get_logger():
    """Return the configured application logger."""
    return logger
