
+"""Discovery pipeline: query generation, crawl, signal detection, extraction."""
+
+from __future__ import annotations
+
+import logging
+
+from bs4 import BeautifulSoup
+import requests
+
+from data.models import DiscoveredPage, JobRecord
+from services.ingestion.search_discovery import generate_search_queries, search_engine_urls
+from services.ingestion.web_fetcher import crawl_seed_urls, fetch_pages
+from services.parsing.hiring_signal_detector import detect_hiring_signal
+from services.parsing.job_extractor import extract_job_record
+from utils.storage import write_json
+
+logger = logging.getLogger(__name__)
+
+SEED_URLS = [
+    "https://news.ycombinator.com/",
+    "https://www.reddit.com/r/forhire/",
+    "https://remoteok.com/",
+    "https://weworkremotely.com/",
+]
+
+
+def _extract_result_links(search_page_html: str) -> list[str]:
+    soup = BeautifulSoup(search_page_html, "html.parser")
+    links: list[str] = []
+    for anchor in soup.select("a.result__a"):
+        href = anchor.get("href", "")
+        if href.startswith("http"):
+            links.append(href)
+    return links
+
+
+def _collect_urls_from_search(queries: list[str], max_links_per_query: int = 6) -> list[str]:
+    all_urls: list[str] = []
+    for query in queries:
+        for surl in search_engine_urls(query, max_results=1):
+            try:
+                response = requests.get(surl, timeout=20)
+                response.raise_for_status()
+                links = _extract_result_links(response.text)[:max_links_per_query]
+                all_urls.extend(links)
+            except Exception as exc:
+                logger.warning("Search crawl failed for '%s': %s", query, exc)
+    return sorted(set(all_urls))
+
+
+def _serialize_raw_pages(pages: list[DiscoveredPage]) -> list[dict]:
+    payload: list[dict] = []
+    for page in pages:
+        payload.append(
+            {
+                "source_url": page.source_url,
+                "title": page.title,
+                "text_preview": page.text[:350],
+                "metadata": page.metadata,
+            }
+        )
+    return payload
+
+
+def discovery_pipeline(base_roles: list[str], locations: list[str]) -> list[JobRecord]:
+    """Run end-to-end job discovery and structured extraction."""
+    queries = generate_search_queries(base_roles, locations)
+    search_urls = _collect_urls_from_search(queries)
+    direct_crawl_urls = crawl_seed_urls(SEED_URLS)
+    candidate_urls = sorted(set(search_urls + direct_crawl_urls))
+
+    pages = fetch_pages(candidate_urls)
+
+    jobs: list[JobRecord] = []
+    for page in pages:
+        signal = detect_hiring_signal(page.text)
+        if not signal.is_hiring:
+            continue
+        jobs.append(extract_job_record(page, signal))
+
+    write_json("data/raw_discovered_pages.json", _serialize_raw_pages(pages))
+    write_json("data/discovered_jobs.json", [job.to_dict() for job in jobs])
+    logger.info(
+        "Discovery completed: %s candidate URLs, %s pages fetched, %s jobs extracted",
+        len(candidate_urls),
+        len(pages),
+        len(jobs),
+    )
+    return jobs
