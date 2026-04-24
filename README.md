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
