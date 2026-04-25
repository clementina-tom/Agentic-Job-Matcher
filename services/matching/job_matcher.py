"""Matching engine based on sentence embeddings + skill overlap."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sentence_transformers import SentenceTransformer, util

from data.models import CandidateProfile, JobRecord

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    job: JobRecord
    fit_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    decision: str


class JobMatcher:
    """Compute job/profile fit and application decision."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model: SentenceTransformer | None = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info("Loaded sentence-transformers model: %s", self.model_name)
        except Exception as exc:
            self.model = None
            logger.warning("Embedding model unavailable, using lexical fallback scoring: %s", exc)

    def _semantic_similarity(self, profile_text: str, job_text: str) -> float:
        if not self.model:
            profile_tokens = set(profile_text.lower().split())
            job_tokens = set(job_text.lower().split())
            if not job_tokens:
                return 0.0
            return len(profile_tokens & job_tokens) / len(job_tokens)

        profile_emb = self.model.encode(profile_text, convert_to_tensor=True)
        job_emb = self.model.encode(job_text, convert_to_tensor=True)
        return float(util.cos_sim(profile_emb, job_emb).item())

    def score(self, profile: CandidateProfile, job: JobRecord, threshold: float = 0.45) -> MatchResult:
        """Score a job against a profile and produce apply/skip decision."""
        profile_text = " ".join(profile.skills + profile.experience + profile.projects + [profile.cv_text])
        job_text = f"{job.job_title}\n{job.description}\n{' '.join(job.skills)}"

        profile_emb = self.model.encode(profile_text, convert_to_tensor=True)
        job_emb = self.model.encode(job_text, convert_to_tensor=True)
        similarity = float(util.cos_sim(profile_emb, job_emb).item())

        candidate_skills = {skill.lower() for skill in profile.skills}
        job_skills = {skill.lower() for skill in job.skills}
        matched = sorted(candidate_skills & job_skills)
        missing = sorted(job_skills - candidate_skills)

        fit_score = max(0.0, min(1.0, (similarity + len(matched) / (len(job_skills) + 1)) / 2))
        decision = "apply" if fit_score >= threshold else "skip"

        logger.info("Scored %s at %.2f (%s)", job.source_url, fit_score, decision)
        return MatchResult(
            job=job,
            fit_score=round(fit_score, 3),
            matched_skills=matched,
            missing_skills=missing,
            decision=decision,
        )
