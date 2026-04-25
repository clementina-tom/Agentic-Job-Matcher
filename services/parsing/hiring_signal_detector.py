"""Rule-based hiring signal detector with confidence scoring."""

from __future__ import annotations

import logging
import re

from data.models import HiringSignal

logger = logging.getLogger(__name__)

HIRING_PATTERNS = [
    r"we are hiring",
    r"we're looking for",
    r"join our team",
    r"hiring\s+[a-zA-Z0-9_\-/ ]+",
    r"send your cv",
    r"apply here",
    r"dm me if interested",
    r"careers?",
    r"open roles?",
]


def detect_hiring_signal(text: str) -> HiringSignal:
    """Detect hiring indicators and calculate an MVP confidence score."""
    normalized = text.lower()
    matched: list[str] = []
    for pattern in HIRING_PATTERNS:
        if re.search(pattern, normalized):
            matched.append(pattern)

    confidence = min(1.0, len(matched) / 4)
    signal = HiringSignal(
        is_hiring=len(matched) > 0,
        confidence_score=round(confidence, 2),
        matched_patterns=matched,
    )
    logger.info("Hiring signal: %s (score=%s)", signal.is_hiring, signal.confidence_score)
    return signal
