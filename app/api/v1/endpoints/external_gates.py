"""Externes Gate-Dashboard — Produktiv-API für den Integrationsstatus externer Systeme.

Liefert aggregierten Gate-Status (DATEV, TSE, DMS, Bank/SEPA, ELSTER) für das
Frontend-Dashboard. Kein Schreibzugriff — reine Leseschicht.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/external-gates", tags=["external-gates"])


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


_SYSTEM_META: dict[str, dict[str, Any]] = {
    "datev": {
        "label": "DATEV",
        "description": "Steuerberater-Export (GoBD-Buchführung)",
        "kategorie": "fibu",
        "docs_url": "https://www.datev.de/web/de/datev-shop/zusatzmodule/datev-unternehmen-online/",
    },
    "elster": {
        "label": "ELSTER",
        "description": "Elektronische Steuererklärung (UStVA, Jahreserklärung)",
        "kategorie": "steuer",
        "docs_url": "https://www.elster.de/",
    },
    "tse": {
        "label": "TSE / Kassensicherung",
        "description": "Technische Sicherheitseinrichtung (§146a AO)",
        "kategorie": "pos",
        "docs_url": "https://www.bsi.bund.de/",
    },
    "dsfinvk": {
        "label": "DSFinV-K",
        "description": "Digitale Schnittstelle der Finanzverwaltung für Kassensysteme",
        "kategorie": "pos",
        "docs_url": "https://www.bundesfinanzministerium.de/",
    },
    "dms": {
        "label": "DMS / Paperless-ngx",
        "description": "Dokumentenmanagementsystem (GoBD-konforme Belegarchivierung)",
        "kategorie": "archiv",
        "docs_url": "https://docs.paperless-ngx.com/",
    },
    "bank_sepa": {
        "label": "Bank / SEPA",
        "description": "CAMT-Import & SEPA-Zahlungsträger-Export",
        "kategorie": "fibu",
        "docs_url": "https://www.ebics.de/",
    },
}


def _gate_status(system_id: str, tenant_id: str) -> dict[str, Any]:
    """Simulierter Gate-Status je System — in Produktion gegen echte Adapter ersetzen."""
    # Deterministische Demo-Zustände nach system_id
    demo_states: dict[str, dict[str, Any]] = {
        "datev": {
            "status": "ok",
            "letzter_export": "2026-06-25T04:00:00Z",
            "naechste_faelligkeit": "2026-07-10",
            "offene_buchungsperioden": 0,
            "hinweis": None,
        },
        "elster": {
            "status": "faellig",
            "letzter_export": "2026-05-31T08:15:00Z",
            "naechste_faelligkeit": "2026-07-10",
            "offene_meldungen": 1,
            "hinweis": "UStVA Juni 2026 noch nicht übermittelt",
        },
        "tse": {
            "status": "ok",
            "letzte_signatur": "2026-06-25T22:58:00Z",
            "signatur_zaehler": 18420,
            "zertifikat_gueltig_bis": "2028-01-01",
            "hinweis": None,
        },
        "dsfinvk": {
            "status": "ok",
            "letzter_tagesabschluss": "2026-06-25",
            "offene_abschluesse": 0,
            "hinweis": None,
        },
        "dms": {
            "status": "ok",
            "letzte_verbindung": "2026-06-26T01:00:00Z",
            "nicht_archivierte_belege": 3,
            "hinweis": "3 Belege in Nachbearbeitungs-Queue",
        },
        "bank_sepa": {
            "status": "warning",
            "letzter_camt_import": "2026-06-24T06:30:00Z",
            "offene_camt_dateien": 2,
            "ausstehende_sepa_laeufe": 1,
            "hinweis": "CAMT-Import vom 25.06. noch ausstehend",
        },
    }
    state = demo_states.get(system_id, {"status": "unbekannt"})
    meta = _SYSTEM_META[system_id]
    return {
        "system_id": system_id,
        "label": meta["label"],
        "description": meta["description"],
        "kategorie": meta["kategorie"],
        "tenant_id": tenant_id,
        "simulated": True,
        **state,
        "abgerufen_am": _utcnow(),
    }


@router.get(
    "/",
    summary="Alle externen Gate-Status abrufen",
    response_model=dict[str, Any],
)
async def get_all_gates(tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    gates = [_gate_status(sid, tenant_id) for sid in _SYSTEM_META]
    status_counts: dict[str, int] = {}
    for g in gates:
        s = g["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    return {
        "tenant_id": tenant_id,
        "gesamt": len(gates),
        "status_zusammenfassung": status_counts,
        "abgerufen_am": _utcnow(),
        "gates": gates,
    }


@router.get(
    "/{system_id}",
    summary="Gate-Status eines externen Systems abrufen",
    response_model=dict[str, Any],
)
async def get_gate(system_id: str, tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    from fastapi import HTTPException

    if system_id not in _SYSTEM_META:
        raise HTTPException(
            status_code=404,
            detail=f"System '{system_id}' nicht bekannt. Verfügbar: {list(_SYSTEM_META)}",
        )
    return _gate_status(system_id, tenant_id)
