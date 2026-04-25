"""Extract structured job info from noisy page text."""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

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
    "llm",
    "data engineering",
    "airflow",
]


def _extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_apply_link(text: str) -> str:
    links = re.findall(r'https?://[^\s)\]>"\']+', text)
    for link in links:
        lowered = link.lower()
        if any(token in lowered for token in ["apply", "job", "career", "greenhouse", "lever"]):
            return link
    return links[0] if links else ""


def _extract_title(page: DiscoveredPage) -> str:
    heading_match = re.search(
        r"(?:hiring|looking for|role|position)[:\-\s]+([A-Z][A-Za-z0-9\-\s]{3,80})",
        page.text,
        flags=re.IGNORECASE,
    )
    if heading_match:
        return heading_match.group(1).strip()
    if page.title:
        return page.title.strip()
    return "Unknown Role"


def _extract_company(text: str, source_url: str) -> str:
    patterns = [
        r"(?:at|@)\s+([A-Z][A-Za-z0-9& .-]{2,})",
        r"company[:\-\s]+([A-Z][A-Za-z0-9& .-]{2,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    domain = urlparse(source_url).netloc.replace("www.", "")
    return domain.split(".")[0].title() if domain else "Unknown Company"


def _classify_source(source_url: str, text: str) -> str:
    url = source_url.lower()
    content = text.lower()
    if any(token in url for token in ["linkedin", "x.com", "twitter", "reddit", "discord"]):
        return "social"
    if "forum" in url or "thread" in url:
        return "forum"
    if "blog" in url or "medium.com" in url:
        return "blog"
    if any(token in url for token in ["jobs", "job-board", "greenhouse", "lever"]):
        return "job_board"
    if "careers" in url or "career" in content:
        return "company_careers"
    return "unstructured_web"


def extract_job_record(page: DiscoveredPage, signal: HiringSignal) -> JobRecord:
    """Extract structured job details from a discovered page."""
    text = page.text
    title = _extract_title(page)
    company = _extract_company(text, page.source_url)
    email = _extract_email(text)
    apply_url = _extract_apply_link(text)

    skills = [skill for skill in SKILL_KEYWORDS if skill in text.lower()]
    application_method = {
        "email": email,
        "form_url": apply_url,
        "external_link": apply_url,
    }

    return JobRecord(
        source_url=page.source_url,
        job_title=title,
        company=company,
        description=text[:2500],
        skills=skills,
        application_method=application_method,
        hiring_signal=signal,
        source_type=_classify_source(page.source_url, text),
    )
