"""Data models used across the system."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CandidateProfile:
    name: str
    email: str
    skills: list[str]
    experience: list[str]
    projects: list[str]
    cv_text: str


@dataclass
class DiscoveredPage:
    source_url: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HiringSignal:
    is_hiring: bool
    confidence_score: float
    matched_patterns: list[str]


@dataclass
class JobRecord:
    source_url: str
    job_title: str
    company: str
    description: str
    skills: list[str]
    application_method: dict[str, str]
    hiring_signal: HiringSignal
    source_type: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["hiring_signal"] = asdict(self.hiring_signal)
        return data
