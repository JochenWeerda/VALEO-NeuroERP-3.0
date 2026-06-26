"""INTEGRATION-EVIDENCE-BOARD-001 — GET /admin/quality-evidence/ aggregiert Qualitätsnachweise.

Phase 1: Liest artifacts/release_evidence.json + externe Gates + Drift-Report.
Phase 2 (INTEGRATION-EVIDENCE-BOARD-001.2): Live-Aggregation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/admin/quality-evidence", tags=["admin", "quality"])

REPO_ROOT = Path(__file__).parents[4]
ARTIFACTS = REPO_ROOT / "artifacts"


class DimensionResult(BaseModel):
    dimension: str
    status: str
    detail: str


class QualityEvidenceSummary(BaseModel):
    generated_at: str
    overall_status: str
    dimensions: list[DimensionResult]
    summary: dict[str, int]
    source: str


def _load_release_evidence() -> dict | None:
    path = ARTIFACTS / "release_evidence.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _load_drift_report() -> dict | None:
    path = ARTIFACTS / "doc_drift_report.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


@router.get("/", response_model=QualityEvidenceSummary)
async def get_quality_evidence(
    _tenant_id: str = Depends(get_tenant_id),
) -> QualityEvidenceSummary:
    """Aggregiert verfügbare Qualitätsnachweise aus CI-Artefakten.

    Phase 1: Statische Artefakte (release_evidence.json, doc_drift_report.json).
    Erfordert: agent:read oder admin-Rolle.
    """
    evidence = _load_release_evidence()
    if evidence:
        dimensions = [DimensionResult(**d) for d in evidence.get("dimensions", [])]
        return QualityEvidenceSummary(
            generated_at=evidence.get("generated_at", datetime.now(timezone.utc).isoformat()),
            overall_status=evidence.get("overall_status", "unknown"),
            dimensions=dimensions,
            summary=evidence.get("summary", {}),
            source="artifacts/release_evidence.json",
        )

    # Fallback: nur Drift-Report
    drift = _load_drift_report()
    if drift:
        total = drift.get("summary", {}).get("total_drift_items", -1)
        status = "pass" if total == 0 else "fail" if total > 0 else "unknown"
        return QualityEvidenceSummary(
            generated_at=drift.get("generated_at", datetime.now(timezone.utc).isoformat()),
            overall_status=status,
            dimensions=[DimensionResult(
                dimension="drift",
                status=status,
                detail=f"total_drift_items={total}",
            )],
            summary={"pass": 1 if status == "pass" else 0, "warn": 0, "fail": 1 if status == "fail" else 0},
            source="artifacts/doc_drift_report.json",
        )

    raise HTTPException(
        status_code=503,
        detail="Keine Qualitäts-Artefakte verfügbar. Bitte release_evidence_report.py ausführen.",
    )


@router.get("/drift", response_model=dict)
async def get_drift_status(
    _tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt den aktuellen Doku-Code-Drift-Status zurück."""
    drift = _load_drift_report()
    if not drift:
        raise HTTPException(status_code=503, detail="Drift-Report nicht verfügbar")
    return drift
