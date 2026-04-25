"""Refiner agent: optional feedback loop to improve profile skills over time."""

from __future__ import annotations

from collections import Counter

from core.state import AgentState


def run(state: AgentState) -> AgentState:
    missing = Counter()
    for job in state.matched_jobs:
        for skill in job.get("missing_skills", []):
            missing[skill] += 1

    state.metrics["top_missing_skills"] = [skill for skill, _ in missing.most_common(10)]
    return state
