# Agentic Job Matcher (v2)

Modern multi-agent architecture for job discovery, ranking, and application assistance with strong focus on **speed**, **accuracy**, and **efficiency**.

## Repository tree

```text
Agentic-Job-Matcher/
├── agents/
│   ├── researcher_agent.py
│   ├── matcher_agent.py
│   ├── tailor_agent.py
│   ├── applier_agent.py
│   ├── refiner_agent.py
│   └── supervisor.py
├── core/
│   ├── vector_store.py
│   ├── embeddings.py
│   ├── browser.py
│   └── state.py
├── services/
│   ├── ingestion/
│   ├── parsing/
│   ├── matching/
│   ├── application/
│   └── agents/
├── graphs/
│   └── job_matcher_graph.py
├── data/
│   ├── chroma_db/
│   ├── candidate_profile.json
│   ├── discovered_jobs.json
│   ├── tailored/
│   ├── applications.db
│   └── logs/
├── utils/
│   ├── rate_limiter.py
│   ├── ethical_guardrails.py
│   ├── deduplicator.py
│   ├── logging.py
│   └── helpers.py
├── tests/
├── ui/
├── app/
│   └── main.py
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

## Architecture benefits

### Speed
- Early filtering and deduplication before expensive matching.
- Vector retrieval narrows candidate set before scoring.
- Async-capable singleton browser reduces repeated startup overhead.

### Accuracy
- Multi-agent flow (research -> match -> tailor/apply) enables staged reasoning.
- Hybrid ranking combines vector similarity + deterministic skill signals.
- Hiring-signal extraction supports social/public hiring posts patterns.

### Efficiency (low RAM / low data)
- Persistent ChromaDB (`data/chroma_db`) avoids re-indexing each run.
- Embedding cache with optional quantization cuts memory and CPU usage.
- Stable job hashing prevents duplicate storage and processing.
- SQLite application log avoids loading full historical state in memory.
- Singleton Playwright contexts + stealth patching reduce browser churn and scraping friction.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Run CLI commands:

```bash
python -m app.main discover
python -m app.main match
python -m app.main apply
python -m app.main daily
python -m app.main status
```
