"""Candidate profile loading utilities."""

from __future__ import annotations

import json
from pathlib import Path

from data.models import CandidateProfile


def load_candidate_profile(path: str = "data/candidate_profile.json") -> CandidateProfile:
    """Load candidate profile from JSON storage."""
    profile = json.loads(Path(path).read_text(encoding="utf-8"))
    return CandidateProfile(**profile)
