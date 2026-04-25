"""Graph registry for job matcher workflow."""

from __future__ import annotations

from agents.supervisor import build_graph


def get_job_matcher_graph():
    return build_graph()
