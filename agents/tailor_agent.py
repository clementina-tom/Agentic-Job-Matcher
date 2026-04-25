"""Tailor agent: prepares targeted CV/cover content for high-fit jobs."""

from __future__ import annotations

from pathlib import Path

from core.state import AgentState
from services.application.cv_tailor import tailor_cv


HIGH_FIT_THRESHOLD = 0.68


def run(state: AgentState) -> AgentState:
    assets: list[dict] = []
    for job in state.shortlisted_jobs:
        if float(job.get("fit_score", 0.0)) < HIGH_FIT_THRESHOLD:
            continue
        cv_text = tailor_cv(state.user_profile.cv_text, job.get("description", ""))
        output_path = Path("data/tailored") / f"{job['job_hash']}.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cv_text, encoding="utf-8")
        assets.append({"job_hash": job["job_hash"], "tailored_cv": str(output_path)})

    state.tailored_assets = assets
    return state
