"""Email application execution."""

from __future__ import annotations

import logging

from data.models import CandidateProfile, JobRecord

logger = logging.getLogger(__name__)


def generate_application_email(profile: CandidateProfile, job: JobRecord, tailored_cv: str) -> str:
    """Create an application email body."""
    return (
        f"Subject: Application for {job.job_title}\n\n"
        f"Hi Hiring Team at {job.company},\n\n"
        f"I'm {profile.name} and I'm interested in the {job.job_title} role. "
        f"I bring strengths in {', '.join(profile.skills[:5])}.\n\n"
        "I've attached a tailored CV below for consideration.\n\n"
        f"--- Tailored CV ---\n{tailored_cv[:1200]}\n\n"
        f"Best regards,\n{profile.name}\n{profile.email}"
    )


def send_email_application(to_email: str, email_body: str) -> bool:
    """Mock SMTP sender for MVP. Replace with real SMTP integration in production."""
    if not to_email:
        logger.warning("No target email provided for application")
        return False

    logger.info("[MOCK SMTP] Sending email application to %s", to_email)
    logger.debug("Email body:\n%s", email_body)
    return True
