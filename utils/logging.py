"""Application logging bootstrap."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(path: str = "data/logs/app.log") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(path, encoding="utf-8")],
        force=True,
    )
