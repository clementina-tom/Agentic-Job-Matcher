"""Executable entrypoint for full agentic job discovery and application workflow."""

from __future__ import annotations

from pipelines.application_pipeline import application_pipeline
from pipelines.discovery_pipeline import discovery_pipeline
from pipelines.matching_pipeline import matching_pipeline
from utils.logging_config import configure_logging


def run_all() -> None:
    """Run all pipelines in sequence."""
    configure_logging()
    discovery_pipeline(base_roles=["python engineer", "backend developer"], locations=["remote", "united states"])
    matching_pipeline()
    application_pipeline()


if __name__ == "__main__":
    run_all()
