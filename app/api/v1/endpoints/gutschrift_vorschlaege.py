"""Buchungsvorschlaege fuer Verkaufsgutschriften: ein Agent schlaegt vor, ein Mensch gibt frei (09.11.2026).

Herausgeloest aus ``sales_credit_notes.py``, als die Gutschrift nach DocFlow zog (BELEG-052). Pfade bleiben; die
Pruefung vor der Freigabe vergleicht den Vorschlag mit der Buchungsvorschau der DocFlow-Gutschrift
(``app/services/gutschrift_docflow.py``). Gebucht wird danach durch ``sales.gutschrift.buchen``.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.finance_roles import beleg_read, beleg_write
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.gutschrift_docflow import vorschau
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/sales", tags=["sales", "credit-notes", "agent-proposals"])


VORSCHLAG_ART = "sales_credit_note_buchung"


class BuchungsvorschlagOut(BaseModel):
    """Vorschlag eines Agenten, eine Gutschrift zu buchen — mit dem, was gebucht wuerde."""

    proposal_id: str
    credit_note_id: str
    credit_note_number: str
    netto: Decimal
    steuer: Decimal
    brutto: Decimal
    approval_status: str
    vorgeschlagen_von: Optional[str] = None
    vorgeschlagen_am: Optional[datetime] = None
    geprueft_von: Optional[str] = None
    geprueft_am: Optional[datetime] = None
    ablehnungsgrund: Optional[str] = None
    gebucht: bool = False


def _schnappschuss(wert: Any) -> dict[str, Any]:
    if isinstance(wert, str):
        wert = json.loads(wert)
    return wert if isinstance(wert, dict) else {}


def _vorschlag(db: Session, tenant_id: str, proposal_id: str, *, sperren: bool = False):
    """Der Buchungsvorschlag des Mandanten — einen fremden oder einen anderer Art gibt es hier nicht."""
    zeile = db.execute(
        text(
            "SELECT proposal_id, approval_status, context_snapshot, created_at, reviewed_by, reviewed_at, "
            "execution_result FROM public.agent_proposals "
            "WHERE proposal_id = :id AND tenant_id = :tid AND action_type = :art"
            + (" FOR UPDATE" if sperren else "")
        ),  # nosec B608  # reviewed-safe: only fixed FOR UPDATE/empty suffix; id, tenant and action are bound parameters
        {"id": proposal_id, "tid": tenant_id, "art": VORSCHLAG_ART},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Buchungsvorschlag nicht gefunden")
    return zeile


def _vorschlag_out(zeile) -> BuchungsvorschlagOut:
    snap = _schnappschuss(zeile["context_snapshot"])
    return BuchungsvorschlagOut(
        proposal_id=str(zeile["proposal_id"]),
        credit_note_id=str(snap.get("credit_note_id") or ""),
        credit_note_number=str(snap.get("credit_note_number") or ""),
        netto=Decimal(str(snap.get("netto") or 0)),
        steuer=Decimal(str(snap.get("steuer") or 0)),
        brutto=Decimal(str(snap.get("brutto") or 0)),
        approval_status=str(zeile["approval_status"]),
        vorgeschlagen_von=snap.get("actor_id"),
        vorgeschlagen_am=zeile["created_at"],
        geprueft_von=zeile["reviewed_by"],
        geprueft_am=zeile["reviewed_at"],
        ablehnungsgrund=snap.get("rejection_reason"),
        gebucht=zeile["execution_result"] is not None,
    )


def _pruefe_vorschlag(db: Session, tenant_id: str, proposal_id: str, pruefer: str) -> dict[str, Any]:
    """Was vor Freigabe oder Ablehnung gelten muss. Gibt den Schnappschuss zurueck oder lehnt ab."""
    zeile = _vorschlag(db, tenant_id, proposal_id)
    if zeile["approval_status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Der Vorschlag ist bereits {zeile['approval_status']}.")
    snap = _schnappschuss(zeile["context_snapshot"])
    # Vier Augen: Wer vorgeschlagen hat, gibt nicht frei.
    if str(snap.get("actor_id") or "") == pruefer:
        raise HTTPException(status_code=409, detail="Wer den Vorschlag gemacht hat, kann ihn nicht selbst prüfen.")
    return snap


def _entscheide(db: Session, tenant_id: str, proposal_id: str, *, status: str, pruefer: str,
                ereignis: str, grund: Optional[str] = None) -> None:
    """Schreibt die Entscheidung. Der Schnappschuss behaelt, was der Agent vorgeschlagen hat."""
    zeile = _vorschlag(db, tenant_id, proposal_id, sperren=True)
    if zeile["approval_status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Der Vorschlag ist bereits {zeile['approval_status']}.")
    snap = _schnappschuss(zeile["context_snapshot"])
    jetzt = datetime.now(timezone.utc).isoformat()
    snap["audit_events"] = [*(snap.get("audit_events") or []), {"event": ereignis, "by": pruefer, "occurred_at": jetzt}]
    if grund:
        snap["rejection_reason"] = grund
    db.execute(
        text(
            "UPDATE public.agent_proposals SET approval_status = :status, reviewed_at = NOW(), reviewed_by = :wer, "
            "context_snapshot = CAST(:snap AS json) WHERE proposal_id = :id AND tenant_id = :tid"
        ),
        {"status": status, "wer": pruefer, "snap": json.dumps(snap), "id": proposal_id, "tid": tenant_id},
    )


def _pruefer(nutzer: dict) -> str:
    """Die Kennung des angemeldeten Menschen — aus der geprueften Anmeldung, nie aus der Anfrage."""
    return str(nutzer.get("sub") or "").strip()


@router.get("/credit-notes/buchungsvorschlaege", response_model=List[BuchungsvorschlagOut],
            summary="Buchungsvorschlaege von Agenten zu Gutschriften", dependencies=[Depends(beleg_read)])
async def list_buchungsvorschlaege(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    where = "tenant_id = :tid AND action_type = :art"
    params: dict[str, Any] = {"tid": tenant_id, "art": VORSCHLAG_ART}
    if status:
        where += " AND approval_status = :status"
        params["status"] = status
    zeilen = db.execute(
        text(
            "SELECT proposal_id, approval_status, context_snapshot, created_at, reviewed_by, reviewed_at, "
            f"execution_result FROM public.agent_proposals WHERE {where} "  # nosec B608
            "ORDER BY created_at DESC LIMIT 200"
        ),
        params,
    ).mappings()
    return [_vorschlag_out(z) for z in zeilen]


@router.post("/credit-notes/buchungsvorschlaege/{proposal_id}/actions/freigeben", response_model=MaskActionResult,
             summary="Buchungsvorschlag eines Agenten freigeben (nur Mensch)")
async def action_vorschlag_freigeben(
    proposal_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: dict = Depends(beleg_write),
) -> MaskActionResult:
    """CE fuer sales/gutschrift:vorschlag_freigeben. Freigeben bucht nicht — danach bucht der Agent.

    Geprueft wird vor der Freigabe, ob die Gutschrift noch so gebucht wuerde, wie der Agent sie
    vorgeschlagen hat. Hat sie sich geaendert oder laesst sie sich nicht mehr buchen, gibt es keine
    Freigabe, sondern den Grund.
    """
    pruefer = _pruefer(nutzer)

    async def pruefe(pruef_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> list[dict[str, Any]]:
        snap = _pruefe_vorschlag(pruef_db, tid, entity_id, pruefer)
        plan = vorschau(pruef_db, tid, str(snap.get("credit_note_id") or ""), pruefer)
        if Decimal(str(snap.get("brutto") or 0)) != plan["brutto"]:
            return [{"field": "_entity", "severity": "blocking", "message": (
                f"Die Gutschrift hat sich seit dem Vorschlag geändert (vorgeschlagen {Decimal(str(snap.get('brutto') or 0)):.2f}, "
                f"jetzt {plan['brutto']:.2f}). Bitte neu vorschlagen lassen.")}]
        return []

    async def gib_frei(schreib_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> str:
        _entscheide(schreib_db, tid, entity_id, status="approved", pruefer=pruefer, ereignis="proposal_approved")
        return "Buchungsvorschlag freigegeben. Gebucht wird durch den Agenten aus diesem Vorschlag."

    return await run_delegated_mask_action(
        db, action_key="vorschlag_freigeben", entity_type="agent_proposal", entity_id=proposal_id,
        tenant_id=tenant_id, body=body, check_fn=pruefe, delegate_fn=gib_frei,
        outbox_event_type="sales.credit_note.posting_approved",
    )


@router.post("/credit-notes/buchungsvorschlaege/{proposal_id}/actions/ablehnen", response_model=MaskActionResult,
             summary="Buchungsvorschlag eines Agenten ablehnen (nur Mensch)")
async def action_vorschlag_ablehnen(
    proposal_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: dict = Depends(beleg_write),
) -> MaskActionResult:
    """CE fuer sales/gutschrift:vorschlag_ablehnen. Braucht einen Grund; die Gutschrift bleibt Entwurf."""
    pruefer = _pruefer(nutzer)
    grund = str(body.get("_auditReason") or "").strip()

    async def pruefe(pruef_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> list[dict[str, Any]]:
        _pruefe_vorschlag(pruef_db, tid, entity_id, pruefer)
        return []

    async def lehne_ab(schreib_db: Session, _payload: dict[str, Any], entity_id: str, tid: str) -> str:
        _entscheide(schreib_db, tid, entity_id, status="rejected", pruefer=pruefer,
                    ereignis="proposal_rejected", grund=grund)
        return "Buchungsvorschlag abgelehnt. Die Gutschrift bleibt Entwurf."

    return await run_delegated_mask_action(
        db, action_key="vorschlag_ablehnen", entity_type="agent_proposal", entity_id=proposal_id,
        tenant_id=tenant_id, body=body, check_fn=pruefe, delegate_fn=lehne_ab,
        outbox_event_type="sales.credit_note.posting_rejected", require_audit_reason=True,
    )
