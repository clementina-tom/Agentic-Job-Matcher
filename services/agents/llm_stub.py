"""LLM-style generation stubs for offline MVP behavior."""

from __future__ import annotations


def generate_text(prompt: str, max_chars: int = 2400) -> str:
    """Return deterministic pseudo-LLM output for MVP/testing."""
    return (
        "[LLM_STUB_OUTPUT]\n"
        "This is a generated draft optimized for the target role.\n"
        f"Prompt summary: {prompt[: max_chars - 100]}"
    )[:max_chars]
