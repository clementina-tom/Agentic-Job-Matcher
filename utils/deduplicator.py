"""Deduplication helpers for discovered jobs."""

from __future__ import annotations

import hashlib
from typing import Any


KEY_FIELDS = ["source_url", "job_title", "company"]


def stable_job_hash(job: dict[str, Any]) -> str:
    payload = "|".join(str(job.get(field, "")).strip().lower() for field in KEY_FIELDS)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def deduplicate_jobs(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for job in jobs:
        job_hash = job.get("job_hash") or stable_job_hash(job)
        if job_hash in seen:
            continue
        seen.add(job_hash)
        row = dict(job)
        row["job_hash"] = job_hash
        output.append(row)
    return output
