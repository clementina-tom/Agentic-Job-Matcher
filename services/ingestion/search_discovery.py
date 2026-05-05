
+"""Search-driven discovery for job-related pages without official APIs."""
+
+from __future__ import annotations
+
+import logging
+from urllib.parse import quote_plus
+
+logger = logging.getLogger(__name__)
+
+SOURCE_FOCUSES = [
+    "job board",
+    "company careers",
+    "engineering blog",
+    "forum thread hiring",
+    "community post hiring",
+    "public post hiring",
+]
+
+
+def generate_search_queries(base_roles: list[str], locations: list[str]) -> list[str]:
+    """Generate broad web search queries for both structured and unstructured sources."""
+    hiring_markers = [
+        '"we are hiring"',
+        '"join our team"',
+        '"apply here"',
+        '"send your cv"',
+        '"dm me if interested"',
+    ]
+
+    queries: list[str] = []
+    for role in base_roles:
+        for location in locations:
+            for focus in SOURCE_FOCUSES:
+                queries.append(f"{role} {location} {focus}")
+            for marker in hiring_markers:
+                queries.append(f"{role} {location} {marker}")
+
+    deduped = sorted(set(queries))
+    logger.info("Generated %s search queries", len(deduped))
+    return deduped
+
+
+def generate_boolean_queries(base_roles: list[str], locations: list[str]) -> list[str]:
+    """Generate advanced boolean search strings for better search-engine retrieval.
+
+    These can be used with standard engines and metasearch providers.
+    """
+    queries: list[str] = []
+    role_expr = " OR ".join(f'"{role}"' for role in base_roles)
+    location_expr = " OR ".join(f'"{location}"' for location in locations)
+    hiring_expr = '"we are hiring" OR "open role" OR "join our team" OR "apply here" OR "send your cv"'
+
+    domains = [
+        "linkedin.com/jobs",
+        "reddit.com",
+        "news.ycombinator.com",
+        "greenhouse.io",
+        "lever.co",
+    ]
+
+    queries.append(f"({role_expr}) AND ({location_expr}) AND ({hiring_expr})")
+    for domain in domains:
+        queries.append(f"({role_expr}) AND ({hiring_expr}) site:{domain}")
+
+    deduped = sorted(set(queries))
+    logger.info("Generated %s boolean queries", len(deduped))
+    return deduped
+
+
+def search_engine_urls(query: str, max_results: int = 4) -> list[str]:
+    """Build DuckDuckGo HTML search URLs to crawl in pages."""
+    encoded = quote_plus(query)
+    return [f"https://html.duckduckgo.com/html/?q={encoded}&s={i * 30}" for i in range(max_results)]
