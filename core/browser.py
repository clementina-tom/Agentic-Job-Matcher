"""Async singleton Playwright browser manager for low-overhead automation."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from playwright_stealth import stealth_async

logger = logging.getLogger(__name__)
ENABLE_STEALTH = os.getenv("AJM_PLAYWRIGHT_STEALTH", "true").lower() == "true"


class BrowserSingleton:
    """Manages one Playwright instance and one browser process per worker."""

    _instance: "BrowserSingleton | None" = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    @classmethod
    async def get_instance(cls) -> "BrowserSingleton":
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            if cls._instance._browser is None:
                await cls._instance._start()
            return cls._instance

    async def _start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        logger.info("Started shared Playwright browser")

    async def new_context(self) -> BrowserContext:
        if self._browser is None:
            await self._start()
        assert self._browser is not None
        context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (compatible; AgenticJobMatcher/2.0)",
            viewport={"width": 1366, "height": 768},
        )
        return context

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Closed shared Playwright browser")


@asynccontextmanager
async def browser_page() -> Page:
    """Context manager yielding an isolated page backed by singleton browser process."""
    singleton = await BrowserSingleton.get_instance()
    context = await singleton.new_context()
    page = await context.new_page()
    if ENABLE_STEALTH:
        await stealth_async(page)
    try:
        yield page
    finally:
        await context.close()
