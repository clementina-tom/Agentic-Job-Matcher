"""Form-based application execution using Playwright."""

from __future__ import annotations

import logging

from playwright.sync_api import sync_playwright

from data.models import CandidateProfile

logger = logging.getLogger(__name__)


def apply_via_form(form_url: str, profile: CandidateProfile, cv_file_path: str = "data/tailored_cv.txt") -> bool:
    """Basic MVP form filler for common fields and submit action."""
    if not form_url:
        logger.warning("No form URL provided")
        return False

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(form_url, wait_until="domcontentloaded", timeout=30000)

            selectors = {
                "name": ["input[name*='name']", "input[id*='name']"],
                "email": ["input[type='email']", "input[name*='email']"],
                "cv": ["input[type='file']"],
            }

            for sel in selectors["name"]:
                if page.locator(sel).count() > 0:
                    page.fill(sel, profile.name)
                    break
            for sel in selectors["email"]:
                if page.locator(sel).count() > 0:
                    page.fill(sel, profile.email)
                    break
            for sel in selectors["cv"]:
                if page.locator(sel).count() > 0:
                    page.set_input_files(sel, cv_file_path)
                    break

            submit_candidates = ["button[type='submit']", "input[type='submit']", "button:has-text('Apply')"]
            for sel in submit_candidates:
                if page.locator(sel).count() > 0:
                    page.click(sel)
                    logger.info("Submitted form at %s", form_url)
                    break

            browser.close()
            return True
    except Exception as exc:
        logger.warning("Form application failed for %s: %s", form_url, exc)
        return False
