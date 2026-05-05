"""Shared utility helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str, default: Any = None) -> Any:
    file = Path(path)
    if not file.exists():
        return default
    return json.loads(file.read_text(encoding="utf-8"))


def write_json(path: str, payload: Any) -> None:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
