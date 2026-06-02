"""In-process job- and progress-tracking for the GAP ETL pipeline.

Die GAP-Pipeline läuft in einem Hintergrund-Thread desselben Prozesses
(``run-year`` startet ``threading.Thread``). Fortschritt wird daher in einem
prozesslokalen, thread-sicheren Dictionary gehalten und über
``GET /gap/pipeline/progress/{job_id}`` abgefragt.

Hinweis: Bei mehreren Worker-Prozessen (Gunicorn/Uvicorn ``--workers > 1``)
ist der Status nicht prozessübergreifend sichtbar. Für den dokumentierten
Einzelprozess-/Dev-Betrieb (siehe ``docs/gap-annual-playbook.md``) ist das
ausreichend; für echten Mehrprozessbetrieb müsste der Store auf Redis o.ä.
umgestellt werden.

Öffentliche API (von ``gap_pipeline_service`` erwartet):
    create_pipeline_job(year) -> job_id
    get_pipeline_progress(job_id) -> dict | None
    class PipelineProgress(job_id, year):
        update_status(step, step_num, total_steps, message, status="running")
        complete(message)
        error(message)
        get_status() -> dict
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

# Anzahl der Pipeline-Schritte (import, aggregate, match, snapshot, hydrate + Start).
DEFAULT_TOTAL_STEPS = 6

_LOCK = threading.Lock()
_JOBS: dict[str, dict[str, Any]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_pipeline_job(year: int, total_steps: int = DEFAULT_TOTAL_STEPS) -> str:
    """Legt einen neuen Pipeline-Job an und liefert dessen Job-ID."""
    job_id = str(uuid4())
    with _LOCK:
        _JOBS[job_id] = {
            "job_id": job_id,
            "year": year,
            "current_step": "queued",
            "progress": 0,
            "total_steps": total_steps,
            "percentage": 0,
            "message": "Job angelegt, wartet auf Start...",
            "status": "running",
            "updated_at": _now_iso(),
            "steps": {},
        }
    return job_id


def get_pipeline_progress(job_id: str) -> Optional[dict[str, Any]]:
    """Liefert eine Kopie des Job-Status oder ``None``, wenn unbekannt."""
    with _LOCK:
        job = _JOBS.get(job_id)
        if job is None:
            return None
        # flache Kopie inkl. tiefer Kopie des steps-Dicts
        snapshot = dict(job)
        snapshot["steps"] = {k: dict(v) for k, v in job["steps"].items()}
        return snapshot


def _prune_locked(max_jobs: int = 200) -> None:
    """Hält den In-Memory-Store klein (älteste Jobs zuerst entfernen)."""
    if len(_JOBS) <= max_jobs:
        return
    ordered = sorted(_JOBS.items(), key=lambda kv: kv[1]["updated_at"])
    for job_id, _ in ordered[: len(_JOBS) - max_jobs]:
        _JOBS.pop(job_id, None)


class PipelineProgress:
    """Schreibzugriff auf den Fortschritt eines einzelnen Jobs."""

    def __init__(self, job_id: str, year: int, total_steps: int = DEFAULT_TOTAL_STEPS) -> None:
        self.job_id = job_id
        self.year = year
        self.total_steps = total_steps
        # Falls der Job (z.B. nach Prozess-Neustart) nicht existiert: anlegen.
        with _LOCK:
            if job_id not in _JOBS:
                _JOBS[job_id] = {
                    "job_id": job_id,
                    "year": year,
                    "current_step": "queued",
                    "progress": 0,
                    "total_steps": total_steps,
                    "percentage": 0,
                    "message": "",
                    "status": "running",
                    "updated_at": _now_iso(),
                    "steps": {},
                }
                _prune_locked()

    def _write(self, **fields: Any) -> None:
        with _LOCK:
            job = _JOBS.get(self.job_id)
            if job is None:
                return
            job.update(fields)
            job["updated_at"] = _now_iso()

    def update_status(
        self,
        step: str,
        step_num: int,
        total_steps: int,
        message: str,
        status: str = "running",
    ) -> None:
        total = total_steps or self.total_steps
        percentage = int(round((step_num / total) * 100)) if total else 0
        with _LOCK:
            job = _JOBS.get(self.job_id)
            if job is None:
                return
            job["current_step"] = step
            job["progress"] = step_num
            job["total_steps"] = total
            job["percentage"] = max(0, min(100, percentage))
            job["message"] = message
            job["status"] = status
            job["updated_at"] = _now_iso()
            job["steps"][step] = {
                "status": status,
                "message": message,
                "step_num": step_num,
                "updated_at": job["updated_at"],
            }

    def complete(self, message: str) -> None:
        self._write(
            current_step="completed",
            progress=self.total_steps,
            percentage=100,
            message=message,
            status="completed",
        )
        with _LOCK:
            job = _JOBS.get(self.job_id)
            if job is not None:
                job["steps"]["completed"] = {
                    "status": "completed",
                    "message": message,
                    "updated_at": _now_iso(),
                }

    def error(self, message: str) -> None:
        self._write(current_step="error", message=message, status="error")
        with _LOCK:
            job = _JOBS.get(self.job_id)
            if job is not None:
                job["steps"]["error"] = {
                    "status": "error",
                    "message": message,
                    "updated_at": _now_iso(),
                }

    def get_status(self) -> dict[str, Any]:
        return get_pipeline_progress(self.job_id) or {}
