"""Search-driven discovery for job-related pages without official APIs."""

from __future__ import annotations

import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


def generate_search_queries(base_roles: list[str], locations: list[str]) -> list[str]:
    """Generate broad web search queries for job discovery."""
    modifiers = [
        '"we are hiring"',
        '"join our team"',
        '"careers"',
        '"apply here"',
        '"hiring"',
    ]
    queries: list[str] = []
    for role in base_roles:
        for location in locations:
            for mod in modifiers:
                queries.append(f"{role} {location} {mod}")
    logger.info("Generated %s search queries", len(queries))
    return queries


def search_engine_urls(query: str, max_results: int = 5) -> list[str]:
    """Build search result page URLs from DuckDuckGo HTML endpoint.

    The consumer should crawl these pages and extract result links.
    """
    encoded = quote_plus(query)
    urls = [f"https://html.duckduckgo.com/html/?q={encoded}&s={i * 30}" for i in range(max_results)]
    return urls
