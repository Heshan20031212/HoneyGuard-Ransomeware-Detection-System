"""
HoneyGuard Centralized Logging Module
Provides console and file logging with structured format.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from honeyguard.utils.paths import get_logs_dir

_LOGGER_INITIALIZED = False


def setup_logger(name: str = "HoneyGuard", log_level: str = None) -> logging.Logger:
    """Configure and return the system logger."""
    global _LOGGER_INITIALIZED

    logger = logging.getLogger(name)
    if _LOGGER_INITIALIZED:
        return logger

    level_str = (log_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating)
    try:
        log_file = get_logs_dir() / "honeyguard.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as exc:
        print(f"Failed to initialize rotating file handler: {exc}", file=sys.stderr)

    _LOGGER_INITIALIZED = True
    return logger


def get_logger(name: str = "HoneyGuard") -> logging.Logger:
    """Retrieve existing logger or configure default."""
    return logging.getLogger(name) if _LOGGER_INITIALIZED else setup_logger(name)
