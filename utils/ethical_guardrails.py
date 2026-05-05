"""Ethical and safety checks before automation actions."""

from __future__ import annotations

from urllib.parse import urlparse


BLOCKED_DOMAINS = {"example-blocked-domain.com"}


def is_allowed_url(url: str) -> bool:
    domain = urlparse(url).netloc.lower().replace("www.", "")
    return bool(domain) and domain not in BLOCKED_DOMAINS


def should_auto_apply(job: dict) -> bool:
    """Default safety gating for automatic application actions."""
    if job.get("fit_score", 0.0) < 0.6:
        return False
    return is_allowed_url(job.get("source_url", ""))
