"""LangGraph shared state schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CandidateProfileState(BaseModel):
    name: str = ""
    email: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    cv_text: str = ""


class AgentState(BaseModel):
    """Mutable state passed between agents in the graph."""

    user_profile: CandidateProfileState = Field(default_factory=CandidateProfileState)
    queries: list[str] = Field(default_factory=list)
    discovered_jobs: list[dict[str, Any]] = Field(default_factory=list)
    deduped_jobs: list[dict[str, Any]] = Field(default_factory=list)
    matched_jobs: list[dict[str, Any]] = Field(default_factory=list)
    shortlisted_jobs: list[dict[str, Any]] = Field(default_factory=list)
    tailored_assets: list[dict[str, Any]] = Field(default_factory=list)
    application_results: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
