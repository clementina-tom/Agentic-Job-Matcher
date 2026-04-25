"""Search-driven discovery for job-related pages without official APIs."""

from __future__ import annotations

import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

SOURCE_FOCUSES = [
    "job board",
    "company careers",
    "engineering blog",
    "forum thread hiring",
    "community post hiring",
    "public post hiring",
]


def generate_search_queries(base_roles: list[str], locations: list[str]) -> list[str]:
    """Generate broad web search queries for both structured and unstructured sources."""
    hiring_markers = [
        '"we are hiring"',
        '"join our team"',
        '"apply here"',
        '"send your cv"',
        '"dm me if interested"',
    ]

    queries: list[str] = []
    for role in base_roles:
        for location in locations:
            for focus in SOURCE_FOCUSES:
                queries.append(f"{role} {location} {focus}")
            for marker in hiring_markers:
                queries.append(f"{role} {location} {marker}")

    deduped = sorted(set(queries))
    logger.info("Generated %s search queries", len(deduped))
    return deduped


def search_engine_urls(query: str, max_results: int = 4) -> list[str]:
    """Build DuckDuckGo HTML search URLs to crawl in pages."""
    encoded = quote_plus(query)
    return [f"https://html.duckduckgo.com/html/?q={encoded}&s={i * 30}" for i in range(max_results)]
