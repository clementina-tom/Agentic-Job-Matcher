"""Matcher agent: fast retrieval + scoring."""

from __future__ import annotations

from core.state import AgentState
from core.vector_store import JobVectorStore
from data.models import HiringSignal, JobRecord
from services.matching.job_matcher import JobMatcher


def run(state: AgentState) -> AgentState:
    profile = state.user_profile
    store = JobVectorStore()
    store.add_jobs(state.deduped_jobs)

    query = " ".join(profile.skills + profile.experience + profile.projects)
    candidates = store.similarity_search(query_text=query, top_k=25)

    matcher = JobMatcher()
    ranked: list[dict] = []

    candidate_index = {job.get("job_hash"): job for job in state.deduped_jobs}
    for row in candidates:
        job = candidate_index.get(row["job_id"])
        if not job:
            continue
        signal_data = job.get("hiring_signal", {})
        job_record = JobRecord(
            source_url=job.get("source_url", ""),
            job_title=job.get("job_title", "Unknown Role"),
            company=job.get("company", "Unknown Company"),
            description=job.get("description", ""),
            skills=job.get("skills", []),
            application_method=job.get("application_method", {}),
            hiring_signal=HiringSignal(
                is_hiring=signal_data.get("is_hiring", True),
                confidence_score=float(signal_data.get("confidence_score", 0.0)),
                matched_patterns=signal_data.get("matched_patterns", []),
            ),
            source_type=job.get("source_type", "unknown"),
        )
        scored = matcher.score(profile=profile, job=job_record)
        ranked.append(
            {
                **job,
                "fit_score": scored.fit_score,
                "decision": scored.decision,
                "matched_skills": scored.matched_skills,
                "missing_skills": scored.missing_skills,
            }
        )

    state.matched_jobs = ranked
    state.shortlisted_jobs = [j for j in ranked if j.get("decision") == "apply"]
    state.metrics["shortlisted"] = len(state.shortlisted_jobs)
    return state
