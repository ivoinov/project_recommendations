import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO"):
    """Configure JSON structured logging for production environments."""

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers = []

    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (stdout for container logging)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
