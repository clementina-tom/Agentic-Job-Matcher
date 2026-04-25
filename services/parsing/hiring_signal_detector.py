"""Rule-based hiring signal detector with confidence scoring."""

from __future__ import annotations

import logging
import re

from data.models import HiringSignal

logger = logging.getLogger(__name__)

PATTERN_WEIGHTS: list[tuple[str, float]] = [
    (r"we are hiring", 0.28),
    (r"we're looking for", 0.22),
    (r"join our team", 0.15),
    (r"hiring\s+[a-zA-Z0-9_\-/ ]+", 0.20),
    (r"send your cv|send your resume", 0.25),
    (r"apply here|application form", 0.25),
    (r"dm me if interested|message me if interested", 0.20),
    (r"careers?|open roles?|vacancies", 0.12),
]


def detect_hiring_signal(text: str) -> HiringSignal:
    """Detect hiring indicators and calculate an MVP confidence score."""
    normalized = text.lower()
    matched: list[str] = []
    confidence = 0.0

    for pattern, weight in PATTERN_WEIGHTS:
        if re.search(pattern, normalized):
            matched.append(pattern)
            confidence += weight

    signal = HiringSignal(
        is_hiring=bool(matched),
        confidence_score=round(min(confidence, 1.0), 2),
        matched_patterns=matched,
    )
    logger.info("Hiring signal: %s (score=%s)", signal.is_hiring, signal.confidence_score)
    return signal
