"""CV tailoring service."""

from __future__ import annotations

from services.agents.llm_stub import generate_text


def tailor_cv(original_cv: str, job_description: str) -> str:
    """Generate a tailored CV using an LLM-style stub function."""
    prompt = (
        "Rewrite the CV bullets to match this job description while remaining truthful.\n\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        f"ORIGINAL CV:\n{original_cv}"
    )
    return generate_text(prompt)
