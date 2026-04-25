"""Application pipeline: tailor CV and apply via email or form."""

from __future__ import annotations

import logging
from pathlib import Path

from data.models import JobRecord, HiringSignal
from services.application.cv_tailor import tailor_cv
from services.application.email_applicator import generate_application_email, send_email_application
from services.application.form_applicator import apply_via_form
from services.matching.profile_loader import load_candidate_profile
from utils.storage import read_json, write_json

logger = logging.getLogger(__name__)


def _job_from_match_payload(payload: dict) -> JobRecord:
    job_payload = payload["job"]
    signal = HiringSignal(**job_payload.get("hiring_signal", {}))
    return JobRecord(
        source_url=job_payload.get("source_url", ""),
        job_title=job_payload.get("job_title", "Unknown Role"),
        company=job_payload.get("company", "Unknown Company"),
        description=job_payload.get("description", ""),
        skills=job_payload.get("skills", []),
        application_method=job_payload.get("application_method", {}),
        hiring_signal=signal,
    )


def application_pipeline() -> list[dict]:
    """Execute job applications for selected jobs."""
    selected_jobs = read_json("data/selected_jobs.json")
    profile = load_candidate_profile()
    results: list[dict] = []

    for payload in selected_jobs:
        job = _job_from_match_payload(payload)
        tailored_cv = tailor_cv(profile.cv_text, job.description)
        cv_path = Path("data/tailored_cv.txt")
        cv_path.write_text(tailored_cv, encoding="utf-8")

        email = job.application_method.get("email", "")
        form_url = job.application_method.get("form_url", "")

        applied = False
        channel = "none"
        if email:
            email_body = generate_application_email(profile, job, tailored_cv)
            applied = send_email_application(email, email_body)
            channel = "email"
        elif form_url:
            applied = apply_via_form(form_url, profile, str(cv_path))
            channel = "form"

        results.append(
            {
                "job_url": job.source_url,
                "job_title": job.job_title,
                "channel": channel,
                "applied": applied,
            }
        )

    write_json("data/application_results.json", results)
    logger.info("Application pipeline finished with %s attempts", len(results))
    return results
