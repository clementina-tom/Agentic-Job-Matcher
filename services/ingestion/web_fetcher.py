"""Fetch web pages using static requests and dynamic Playwright rendering."""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from data.models import DiscoveredPage

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; AgenticJobDiscovery/1.0)"
DEFAULT_TIMEOUT = 15


def fetch_static_page(url: str, timeout: int = DEFAULT_TIMEOUT) -> DiscoveredPage | None:
    """Fetch and parse a mostly-static page with requests and BeautifulSoup."""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = (soup.title.text or "").strip() if soup.title else ""
        text = soup.get_text(" ", strip=True)
        return DiscoveredPage(
            source_url=url,
            title=title,
            text=text,
            metadata={"fetch_mode": "static", "html": response.text},
        )
    except Exception as exc:
        logger.warning("Static fetch failed for %s: %s", url, exc)
        return None


def fetch_dynamic_page(url: str, timeout_ms: int = 30000) -> DiscoveredPage | None:
    """Fetch page content using Playwright for JavaScript-rendered pages."""
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            page.wait_for_timeout(1200)
            title = page.title()
            text = page.inner_text("body")
            html = page.content()
            browser.close()
        return DiscoveredPage(
            source_url=url,
            title=title,
            text=text,
            metadata={"fetch_mode": "dynamic", "html": html},
        )
    except Exception as exc:
        logger.warning("Dynamic fetch failed for %s: %s", url, exc)
        return None


def fetch_page(url: str) -> DiscoveredPage | None:
    """Fetch with static-first, dynamic-fallback strategy."""
    page = fetch_static_page(url)
    if page:
        logger.info("Fetched static page: %s", url)
        return page

    fallback = fetch_dynamic_page(url)
    if fallback:
        logger.info("Fetched dynamic page: %s", url)
    return fallback


def fetch_pages(urls: list[str]) -> list[DiscoveredPage]:
    """Fetch a list of pages with graceful error handling."""
    pages: list[DiscoveredPage] = []
    for url in urls:
        page = fetch_page(url)
        if page:
            pages.append(page)
    logger.info("Fetched %s/%s pages", len(pages), len(urls))
    return pages


def extract_links(page: DiscoveredPage, same_domain_only: bool = True) -> list[str]:
    """Extract crawlable links from page metadata HTML when available."""
    html = page.metadata.get("html", "")
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    src_domain = urlparse(page.source_url).netloc
    links: list[str] = []
    for a_tag in soup.select("a[href]"):
        href = a_tag.get("href", "")
        absolute = urljoin(page.source_url, href)
        if not absolute.startswith("http"):
            continue
        if same_domain_only and urlparse(absolute).netloc != src_domain:
            continue
        links.append(absolute)

    return sorted(set(links))


def crawl_seed_urls(seed_urls: list[str], max_links_per_seed: int = 10) -> list[str]:
    """Direct crawling entrypoint for company pages/blogs/forums/social-like pages."""
    discovered: list[str] = []
    for seed in seed_urls:
        page = fetch_page(seed)
        if not page:
            continue
        links = extract_links(page, same_domain_only=False)
        discovered.extend(links[:max_links_per_seed])

    deduped = sorted(set(seed_urls + discovered))
    logger.info("Direct crawl discovered %s URLs from %s seeds", len(deduped), len(seed_urls))
    return deduped
