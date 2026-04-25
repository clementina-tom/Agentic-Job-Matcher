"""Logging helpers for consistent structured logs."""

import logging
from pathlib import Path


def configure_logging(log_file: str = "data/pipeline.log") -> None:
    """Configure root logger for console + file output."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )
