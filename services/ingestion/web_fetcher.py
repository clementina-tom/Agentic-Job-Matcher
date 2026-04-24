"""Fetch web pages using static requests and dynamic Playwright rendering."""

from __future__ import annotations

import logging
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from data.models import DiscoveredPage

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; AgenticJobDiscovery/1.0)"


def fetch_static_page(url: str, timeout: int = 15) -> DiscoveredPage | None:
    """Fetch and parse a mostly-static page with requests and BeautifulSoup."""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = (soup.title.text or "").strip() if soup.title else ""
        text = soup.get_text(" ", strip=True)
        logger.info("Fetched static page: %s", url)
        return DiscoveredPage(source_url=url, title=title, text=text)
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
        logger.info("Fetched dynamic page: %s", url)
        return DiscoveredPage(source_url=url, title=title, text=text, metadata={"html": html})
    except Exception as exc:
        logger.warning("Dynamic fetch failed for %s: %s", url, exc)
        return None


def fetch_pages(urls: Iterable[str]) -> list[DiscoveredPage]:
    """Try static fetch first, then dynamic fallback for failures."""
    url_list = list(urls)
    pages: list[DiscoveredPage] = []
    for url in url_list:
        page = fetch_static_page(url)
        if page is None:
            page = fetch_dynamic_page(url)
        if page:
            pages.append(page)
    logger.info("Fetched %s/%s pages", len(pages), len(url_list))
    return pages
