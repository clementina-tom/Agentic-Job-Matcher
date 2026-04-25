"""Applier agent: controlled auto-apply flow with guardrails."""

from __future__ import annotations

from core.state import AgentState
from data.models import HiringSignal, JobRecord
from services.application.email_applicator import generate_application_email, send_email_application
from utils.ethical_guardrails import should_auto_apply


def run(state: AgentState) -> AgentState:
    results: list[dict] = []
    for job in state.shortlisted_jobs:
        if not should_auto_apply(job):
            results.append({"job_hash": job.get("job_hash"), "status": "skipped_guardrail"})
            continue

        email = job.get("application_method", {}).get("email", "")
        if email:
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
            body = generate_application_email(state.user_profile, job_record, "See tailored CV attached")
            sent = send_email_application(email, body)
            results.append({"job_hash": job.get("job_hash"), "status": "applied" if sent else "failed", "channel": "email"})
        else:
            results.append({"job_hash": job.get("job_hash"), "status": "manual_required", "channel": "form_or_external"})

    state.application_results = results
    return state
