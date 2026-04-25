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
# Agentic Job Discovery and Application System (MVP)

A modular Python MVP that discovers job opportunities from open-web sources (no official APIs), detects hiring signals, extracts structured job data, matches roles to a candidate profile, and executes basic applications.

## Architecture

```text
/app
/services
  /ingestion
  /parsing
  /matching
  /application
  /agents
/pipelines
/data
/utils
```

### Core modules

- **Discovery pipeline** (`pipelines/discovery_pipeline.py`)
  - Generates search queries
  - Crawls search results and target pages
  - Detects hiring signals with rules + confidence score
  - Extracts structured job data and stores JSON
- **Matching pipeline** (`pipelines/matching_pipeline.py`)
  - Loads candidate profile from `data/candidate_profile.json`
  - Uses `sentence-transformers` cosine similarity + skill overlap
  - Produces `fit_score` and `apply/skip` decision
- **Application pipeline** (`pipelines/application_pipeline.py`)
  - Tailors CV using LLM-style stub function
  - Applies by email (mock SMTP) or via form automation (Playwright)

## Setup

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
python -m app.main serve --port 8000
```

## UI dashboard

`ui/index.html` now includes a lightweight local dashboard that reads:
- `data/discovered_jobs.json`
- `data/match_results.json`
- `data/application_results.json`

Start API + UI with:

```bash
python -m app.main serve --port 8000
```

Then open:
- `http://localhost:8000/dashboard`
- `http://localhost:8000/api/metrics`
## Run all pipelines

```bash
python -m pipelines.run_all
```

## Output artifacts

- `data/discovered_jobs.json`
- `data/match_results.json`
- `data/selected_jobs.json`
- `data/application_results.json`
- `data/pipeline.log`

## Notes on production hardening beyond MVP

- Add robots.txt compliance and domain allow/deny policies.
- Add retry/backoff, request throttling, and queue-based ingestion.
- Improve extraction with NER/LLM parser and stricter schema validation.
- Integrate secret manager + real SMTP transport.
- Add browser fingerprint rotation and anti-bot safeguards where legally permissible.
- Add persistent state store (Postgres/Elastic) and analytics dashboards.
