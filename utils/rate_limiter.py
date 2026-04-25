"""Simple async rate limiter for network politeness."""

from __future__ import annotations

import asyncio
import time


class AsyncRateLimiter:
    def __init__(self, min_interval_seconds: float = 0.4) -> None:
        self.min_interval_seconds = min_interval_seconds
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            delta = now - self._last
            if delta < self.min_interval_seconds:
                await asyncio.sleep(self.min_interval_seconds - delta)
            self._last = time.monotonic()
