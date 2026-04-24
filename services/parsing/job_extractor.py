"""Extract structured job info from noisy page text."""

from __future__ import annotations

import logging
import re

from data.models import DiscoveredPage, HiringSignal, JobRecord

logger = logging.getLogger(__name__)

SKILL_KEYWORDS = [
    "python",
    "sql",
    "docker",
    "kubernetes",
    "aws",
    "fastapi",
    "django",
    "react",
    "playwright",
    "machine learning",
]


def _extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_first_url(text: str) -> str:
    match = re.search(r'https?://[^\s)\]>"\']+', text)
    return match.group(0) if match else ""


def extract_job_record(page: DiscoveredPage, signal: HiringSignal) -> JobRecord:
    """Extract structured job details from a discovered page."""
    text = page.text
    title = page.title.strip() or "Unknown Role"

    company = "Unknown Company"
    company_match = re.search(r"(?:at|@)\s+([A-Z][A-Za-z0-9& .-]{2,})", text)
    if company_match:
        company = company_match.group(1).strip()

    email = _extract_email(text)
    form_url = _extract_first_url(text)

    skills = [skill for skill in SKILL_KEYWORDS if skill in text.lower()]

    application_method = {
        "email": email,
        "form_url": form_url,
        "external_link": form_url,
    }

    description = text[:1800]

    record = JobRecord(
        source_url=page.source_url,
        job_title=title,
        company=company,
        description=description,
        skills=skills,
        application_method=application_method,
        hiring_signal=signal,
    )
    logger.info("Extracted job record from %s", page.source_url)
    return record
