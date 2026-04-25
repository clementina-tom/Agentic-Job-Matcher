"""Storage helpers for JSON artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: str, payload: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
