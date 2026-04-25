# Agentic Job Discovery and Application System (MVP)

A modular Python MVP that discovers job opportunities from open-web sources (**no official APIs**), detects hiring signals, extracts structured job data, matches roles to a candidate profile, and executes basic applications.

## Project structure

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

## What is implemented end-to-end

### 1) Search & discover jobs (without official APIs)
- Search query generation for structured + unstructured sources (job boards, company careers, blogs, forums, public social-like pages).
- Search result crawling via DuckDuckGo HTML pages.
- Direct crawling from configurable seed URLs.
- Static fetch (`requests` + `BeautifulSoup`) with dynamic fallback (`Playwright`).

### 2) Detect hiring signals
- Rule-based phrase detection.
- Weighted confidence scoring (`0.0` to `1.0`).

### 3) Extract job information
- Extracts: title, company, description, skills, application method (`email`, `form_url`, `external_link`), and source type.
- Stores structured JSON artifacts.

### 4) User profile input
- Uses stored candidate profile in `data/candidate_profile.json`.

### 5) Matching engine
- `sentence-transformers` semantic similarity.
- Skill overlap and missing-skill detection.
- Produces fit score + `apply/skip` decision.
- Graceful lexical fallback if embedding model cannot load.

### 6) CV tailoring
- LLM-style deterministic stub for CV tailoring / keyword optimization.

### 7) Application execution
- Email application path with generated email (mock SMTP send function).
- Form application path with Playwright form fill + submit.
- External-link fallback note for manual completion.

### 8) Pipelines
- `discovery_pipeline()`
- `matching_pipeline()`
- `application_pipeline()`
- `pipelines/run_all.py` executes the full flow.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
python -m pipelines.run_all
```

## Output artifacts

- `data/raw_discovered_pages.json`
- `data/discovered_jobs.json`
- `data/match_results.json`
- `data/selected_jobs.json`
- `data/application_results.json`
- `data/pipeline.log`

## Engineering hardening improvements included
- Consistent logging at every pipeline stage.
- Graceful pipeline behavior when prior-stage artifacts are absent.
- Separation of concerns between ingestion, parsing, matching, and application services.
