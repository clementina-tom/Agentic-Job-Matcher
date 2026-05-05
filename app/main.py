"""Typer CLI for the agentic job matcher system."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import typer
import uvicorn

from agents.supervisor import run_graph
from core.state import AgentState, CandidateProfileState
from utils.helpers import read_json, write_json
from utils.logging import configure_logging

app = typer.Typer(help="Agentic Job Discovery and Application CLI")


def _load_profile(path: str = "data/candidate_profile.json") -> CandidateProfileState:
    raw = read_json(path, default={})
    return CandidateProfileState(**raw)


def _save_applications(rows: list[dict[str, Any]], db_path: str = "data/applications.db") -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_hash TEXT,
            status TEXT,
            channel TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    for row in rows:
        conn.execute(
            "INSERT INTO applications (job_hash, status, channel) VALUES (?, ?, ?)",
            (row.get("job_hash", ""), row.get("status", ""), row.get("channel", "")),
        )
    conn.commit()
    conn.close()


def _run(mode: str) -> AgentState:
    configure_logging()
    state = AgentState(user_profile=_load_profile())
    final_state = run_graph(state)

    if mode in {"discover", "daily", "all"}:
        write_json("data/discovered_jobs.json", final_state.deduped_jobs)
    if mode in {"match", "daily", "all"}:
        write_json("data/match_results.json", final_state.matched_jobs)
    if mode in {"apply", "daily", "all"}:
        write_json("data/application_results.json", final_state.application_results)
        _save_applications(final_state.application_results)

    write_json("data/run_report.json", {"mode": mode, "metrics": final_state.metrics})
    write_json("data/state_snapshot.json", final_state.model_dump())
    return final_state


@app.command()
def discover() -> None:
    """Run discovery stage and persist discovered jobs."""
    state = _run("discover")
    typer.echo(f"Discovered deduped jobs: {len(state.deduped_jobs)}")


@app.command()
def match() -> None:
    """Run matching stage and persist ranking results."""
    state = _run("match")
    typer.echo(f"Matched jobs: {len(state.matched_jobs)} | shortlisted: {len(state.shortlisted_jobs)}")


@app.command()
def apply() -> None:
    """Run application stage and persist outcomes."""
    state = _run("apply")
    typer.echo(f"Application outcomes: {len(state.application_results)}")


@app.command()
def daily() -> None:
    """Run full daily workflow."""
    state = _run("daily")
    typer.echo(
        f"Daily run complete | discovered={len(state.deduped_jobs)} "
        f"shortlisted={len(state.shortlisted_jobs)} applied={len(state.application_results)}"
    )


@app.command()
def status(db_path: str = "data/applications.db") -> None:
    """Show basic status metrics from SQLite application log."""
    if not Path(db_path).exists():
        typer.echo("No application database found yet.")
        raise typer.Exit(0)

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status ORDER BY COUNT(*) DESC"
    ).fetchall()
    conn.close()

    typer.echo("Application status summary:")
    for status_name, count in rows:
        typer.echo(f"- {status_name}: {count}")


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Start dashboard API server and static UI."""
    uvicorn.run("app.server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
