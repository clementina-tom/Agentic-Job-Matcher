+# Agentic Job Matcher (v2+)
+
+Modern multi-agent architecture for job discovery, ranking, and application assistance with strong focus on **speed**, **accuracy**, and **efficiency**.
+
+## Repository tree
+
+```text
+Agentic-Job-Matcher/
+├── agents/
+├── core/
+├── services/
+├── graphs/
+├── data/
+├── utils/
+├── tests/
+├── ui/
+├── app/
+├── Dockerfile
+├── requirements.txt
+├── README.md
+└── .gitignore
+```
+
+## Original vision
+
+Build an agentic system that:
+1. Discovers hiring opportunities from broad internet sources (job boards + forums + social-like signals).
+2. Matches opportunities to a profile with hybrid scoring.
+3. Tailors only high-fit opportunities.
+4. Applies safely with guardrails and tracks outcomes.
+5. Learns from missing skills over time.
+
+This positions the system closer to products such as ApplyPilot-style workflows while remaining open and extensible.
+
+## Key upgrades implemented
+
+### Discovery + Boolean Search
+- Added boolean query generation (`AND`/`OR` with source constraints) for stronger search-engine retrieval.
+- Preserved direct crawl mode so the system can still discover from seeds if search engine quality drops.
+
+### KPI-oriented metrics
+- Funnel metrics: discovered -> matched -> apply decisions -> application outcomes.
+- Quality metrics: average fit score + high-fit count.
+- Operational metrics: source-type breakdown + application status breakdown.
+
+### UI redesign
+- Dashboard now shows operational funnel, quality indicators, source mix, and failure/status breakdowns.
+- Reduced vanity metrics and improved decision visibility.
+
+### Reliability
+- Added end-to-end graph smoke test with controlled stubs to validate orchestration flow.
+
+## Quick start
+
+```bash
+python -m venv .venv
+source .venv/bin/activate
+pip install -r requirements.txt
+playwright install chromium
+```
+
+Run CLI commands:
+
+```bash
+python -m app.main discover
+python -m app.main match
+python -m app.main apply
+python -m app.main daily
+python -m app.main status
+python -m app.main serve --port 8000
+```
+
+Open dashboard:
+- `http://localhost:8000/dashboard`
+- `http://localhost:8000/api/metrics`
