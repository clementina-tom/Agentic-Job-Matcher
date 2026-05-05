"""Researcher agent: broad web and social hiring discovery."""

from __future__ import annotations

from collections import Counter

from core.state import AgentState
from services.ingestion.search_discovery import generate_boolean_queries, generate_search_queries
from services.ingestion.web_fetcher import crawl_seed_urls, fetch_pages
from services.parsing.hiring_signal_detector import detect_hiring_signal
from services.parsing.job_extractor import extract_job_record
from utils.deduplicator import deduplicate_jobs

SEED_URLS = [
    "https://news.ycombinator.com/",
    "https://www.reddit.com/r/forhire/",
    "https://www.linkedin.com/jobs/",
    "https://x.com/search?q=we%20are%20hiring",
]


def run(state: AgentState) -> AgentState:
    keyword_queries = generate_search_queries(base_roles=["python engineer", "backend developer"], locations=["remote", "usa"])
    boolean_queries = generate_boolean_queries(base_roles=["python engineer", "backend developer"], locations=["remote", "usa"])
    discovered_urls = crawl_seed_urls(SEED_URLS)
    pages = fetch_pages(discovered_urls)

    jobs: list[dict] = []
    for page in pages:
        signal = detect_hiring_signal(page.text)
        if not signal.is_hiring:
            continue
        jobs.append(extract_job_record(page, signal).to_dict())

    deduped = deduplicate_jobs(jobs)
    state.queries = keyword_queries + boolean_queries
    state.discovered_jobs = jobs
    state.deduped_jobs = deduped

    source_counts = Counter(job.get("source_type", "unknown") for job in deduped)
    state.metrics["researcher_total"] = len(deduped)
    state.metrics["source_counts"] = dict(source_counts)
    state.metrics["dedup_rate"] = round(1 - (len(deduped) / len(jobs)), 4) if jobs else 0.0
    return state
