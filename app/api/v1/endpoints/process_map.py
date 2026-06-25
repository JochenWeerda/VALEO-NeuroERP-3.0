"""P2.1 — Workflow-Prozesskarte API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any

from app.services.process_map_service import ProcessDomain, process_map_service

router = APIRouter(prefix="/process-map", tags=["process-map", "workflow"])


@router.get("/", summary="Alle Prozesskarten auflisten", response_model=list[dict[str, Any]])
async def list_domains() -> list[dict[str, Any]]:
    return process_map_service.list_domains()


@router.get("/summary", summary="Prozesskarten-Zusammenfassung", response_model=dict[str, Any])
async def get_summary() -> dict[str, Any]:
    return process_map_service.summary()


@router.get("/external-gates", summary="Externe Gates aller Prozessketten", response_model=list[dict[str, Any]])
async def list_external_gates(domain: str | None = None) -> list[dict[str, Any]]:
    parsed: ProcessDomain | None = None
    if domain:
        try:
            parsed = ProcessDomain(domain)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Unbekannte Domain '{domain}'")
    return process_map_service.list_external_gates(domain=parsed)


@router.get("/external-gates/open", summary="Offene externe Gates", response_model=list[dict[str, Any]])
async def get_open_gates() -> list[dict[str, Any]]:
    return process_map_service.get_open_gates()


@router.get("/{domain}", summary="Prozesskarte fuer Domain", response_model=dict[str, Any])
async def get_process_map(domain: str) -> dict[str, Any]:
    try:
        d = ProcessDomain(domain)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unbekannte Domain '{domain}'. Gueltige Werte: {[d.value for d in ProcessDomain]}")
    try:
        return process_map_service.get_process_map(d).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
