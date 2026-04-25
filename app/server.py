"""FastAPI backend for dashboard and lightweight monitoring endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from utils.helpers import read_json


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UI_DIR = BASE_DIR / "ui"

app = FastAPI(title="Agentic Job Matcher Dashboard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")


def _read_dataset(filename: str) -> list[dict[str, Any]]:
    payload = read_json(str(DATA_DIR / filename), default=[])
    return payload if isinstance(payload, list) else []


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Agentic Job Matcher API", "ui": "/dashboard", "health": "/health"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/dashboard")
def dashboard() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")


@app.get("/api/discovered_jobs")
def discovered_jobs(limit: int = 200) -> dict[str, Any]:
    rows = _read_dataset("discovered_jobs.json")
    return {"count": len(rows), "items": rows[: max(limit, 0)]}


@app.get("/api/match_results")
def match_results(limit: int = 200) -> dict[str, Any]:
    rows = _read_dataset("match_results.json")
    return {"count": len(rows), "items": rows[: max(limit, 0)]}


@app.get("/api/application_results")
def application_results(limit: int = 200) -> dict[str, Any]:
    rows = _read_dataset("application_results.json")
    return {"count": len(rows), "items": rows[: max(limit, 0)]}


@app.get("/api/metrics")
def metrics() -> dict[str, Any]:
    discovered = _read_dataset("discovered_jobs.json")
    matches = _read_dataset("match_results.json")
    applications = _read_dataset("application_results.json")

    apply_decisions = [m for m in matches if m.get("decision") == "apply"]
    avg_fit = 0.0
    if matches:
        fit_scores = [float(m.get("fit_score", 0.0)) for m in matches]
        avg_fit = sum(fit_scores) / len(fit_scores)

    return {
        "discovered_jobs": len(discovered),
        "match_results": len(matches),
        "apply_decisions": len(apply_decisions),
        "application_results": len(applications),
        "avg_fit_score": round(avg_fit, 4),
    }
