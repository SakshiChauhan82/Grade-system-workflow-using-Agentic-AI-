"""Centralized logger for the entire system."""
import logging
import os
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """Return a named logger writing to both file and console."""
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/system_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
