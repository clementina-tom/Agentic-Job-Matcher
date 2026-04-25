"""Matching pipeline: score discovered jobs against candidate profile."""

from __future__ import annotations

import logging

from services.matching.job_matcher import JobMatcher
from services.matching.profile_loader import load_candidate_profile
from utils.storage import read_json, write_json
from data.models import JobRecord, HiringSignal

logger = logging.getLogger(__name__)


def _job_from_dict(payload: dict) -> JobRecord:
    signal_data = payload.get("hiring_signal", {})
    signal = HiringSignal(
        is_hiring=signal_data.get("is_hiring", False),
        confidence_score=signal_data.get("confidence_score", 0.0),
        matched_patterns=signal_data.get("matched_patterns", []),
    )
    return JobRecord(
        source_url=payload.get("source_url", ""),
        job_title=payload.get("job_title", "Unknown Role"),
        company=payload.get("company", "Unknown Company"),
        description=payload.get("description", ""),
        skills=payload.get("skills", []),
        application_method=payload.get("application_method", {}),
        hiring_signal=signal,
    )


def matching_pipeline() -> list[dict]:
    """Load profile and jobs, score them, and filter for applications."""
    if not Path("data/discovered_jobs.json").exists():
        logger.warning("No discovered jobs artifact found; skipping matching")
        write_json("data/match_results.json", [])
        write_json("data/selected_jobs.json", [])
        return []

    profile = load_candidate_profile()
    raw_jobs = read_json("data/discovered_jobs.json")
    jobs = [_job_from_dict(payload) for payload in raw_jobs]

    matcher = JobMatcher()
    matches = []
    for job in jobs:
        result = matcher.score(profile, job)
        matches.append(
            {
                "job": job.to_dict(),
                "fit_score": result.fit_score,
                "matched_skills": result.matched_skills,
                "missing_skills": result.missing_skills,
                "decision": result.decision,
            }
        )

    write_json("data/match_results.json", matches)
    selected = [m for m in matches if m["decision"] == "apply"]
    write_json("data/selected_jobs.json", selected)
    logger.info("Matching pipeline selected %s jobs to apply", len(selected))
    return selected
