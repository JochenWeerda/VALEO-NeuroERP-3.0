"""Klaerliste der Partnerzuordnung (ADR Geschaeftspartnerstamm, Stufe 2).

Die Rueckfuellung ``partner_rueckfuellung_20261101`` ordnet Kunden und Lieferanten nur zu, wenn die
Regel eindeutig ist; Zweifelsfaelle liegen in ``domain_crm.partner_klaerfaelle``. Dieser Weg liest sie
mandantengenau, damit die Studio-Liste ``crm/partner-klaerfaelle-liste`` sie zeigen kann, und entscheidet sie
(Stufe 3) als Zeilenaktion.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(prefix="/crm/partner-klaerfaelle", tags=["crm", "partner"])


class PartnerKlaerfallOut(BaseModel):
    id: str
    quelle: str
    satz_id: str
    nummer: Optional[str] = None
    name: Optional[str] = None
    grund: str
    kandidaten: list[str] = []
    kandidaten_text: Optional[str] = None
    erstellt_am: Optional[str] = None
    erledigt_am: Optional[str] = None


@router.get("", response_model=list[PartnerKlaerfallOut], summary="Klaerfaelle der Partnerzuordnung auflisten")
def list_partner_klaerfaelle(
    erledigt: bool = Query(False, description="Auch erledigte Klaerfaelle zeigen"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    rows = db.execute(
        text("""
            SELECT k.id, k.quelle, k.satz_id, k.grund, k.kandidaten, k.erstellt_am, k.erledigt_am,
                   COALESCE(c.customer_number, l.lieferantennummer) AS nummer,
                   COALESCE(c.company_name, l.firmenname) AS name
            FROM domain_crm.partner_klaerfaelle k
            LEFT JOIN domain_crm.customers c
                   ON k.quelle = 'kunde' AND c.id = k.satz_id AND c.tenant_id = k.tenant_id
            LEFT JOIN domain_einkauf.lieferanten l
                   ON k.quelle = 'lieferant' AND l.id::text = k.satz_id AND l.tenant_id = k.tenant_id
            WHERE k.tenant_id = :tid AND (:erledigt OR k.erledigt_am IS NULL)
            ORDER BY k.erstellt_am, k.id
            LIMIT :limit
        """),
        {"tid": tenant_id, "erledigt": erledigt, "limit": limit},
    ).mappings().fetchmany(limit)
    return [
        {**dict(r), "kandidaten": list(r["kandidaten"] or []), "kandidaten_text": ", ".join(r["kandidaten"] or []),
         "erstellt_am": r["erstellt_am"].isoformat() if r["erstellt_am"] else None,
         "erledigt_am": r["erledigt_am"].isoformat() if r["erledigt_am"] else None}
        for r in rows
    ]


# ── Entscheiden (Stufe 3) ──────────────────────────────────────────────────────────────────────────────────────
# Ein Klaerfall wird fachlich entschieden: einem vorhandenen Partner des Mandanten zuordnen oder bewusst einen neuen
# Partner anlegen. Beides setzt die Verknuepfung am Kunden bzw. Lieferanten, die Rolle am Partner und erledigt den
# Fall; Begruendung, Audit und Ereignis laufen ueber die Maskenaktions-Runtime.

_SATZ = {"kunde": ("domain_crm.customers", "business_partner_id", "id"),
         "lieferant": ("domain_einkauf.lieferanten", "partner_id", "id::text")}


def _offener_fall(session: Session, fall_id: str, tid: str) -> Optional[dict]:
    return session.execute(
        text("SELECT id, quelle, satz_id, kandidaten FROM domain_crm.partner_klaerfaelle "
             "WHERE id = :id AND tenant_id = :tid AND erledigt_am IS NULL"),
        {"id": fall_id, "tid": tid},
    ).mappings().first()


def _satz(session: Session, quelle: str, satz_id: str, tid: str) -> Optional[dict]:
    tabelle, spalte, schluessel = _SATZ[quelle]  # feste Zuordnung je Quelle
    namensspalte = "company_name" if quelle == "kunde" else "firmenname"
    ustspalte = "tax_id" if quelle == "kunde" else "ust_id"
    return session.execute(
        text(f"SELECT {namensspalte} AS name, {ustspalte} AS ust, {spalte} AS partner FROM {tabelle} "  # nosec B608
             f"WHERE {schluessel} = :sid AND tenant_id = :tid"),  # reviewed-safe: Namen aus _SATZ
        {"sid": satz_id, "tid": tid},
    ).mappings().first()


def _erledigen(session: Session, fall: dict, tid: str, partner_id: str) -> None:
    from app.services.business_partner_service import BusinessPartnerService

    tabelle, spalte, schluessel = _SATZ[fall["quelle"]]
    session.execute(
        text(f"UPDATE {tabelle} SET {spalte} = :p WHERE {schluessel} = :sid AND tenant_id = :tid"),  # nosec B608
        {"p": partner_id, "sid": fall["satz_id"], "tid": tid},  # reviewed-safe: Namen aus _SATZ
    )
    # Rolle am Partner setzen (die Bruecke prueft dabei den Mandanten des Partners).
    BusinessPartnerService(session, tid).partner_fuer_rolle(fall["quelle"], name="", partner_id=partner_id)
    session.execute(text("UPDATE domain_crm.partner_klaerfaelle SET erledigt_am = now() WHERE id = :id "
                         "AND tenant_id = :tid"), {"id": fall["id"], "tid": tid})
    session.commit()


def _pruefen_basis(session: Session, fall_id: str, tid: str) -> tuple[Optional[dict], list[dict]]:
    fall = _offener_fall(session, fall_id, tid)
    if fall is None:
        return None, [{"field": "_entity", "message": "Klaerfall nicht gefunden oder schon erledigt.",
                       "severity": "blocking"}]
    if _satz(session, fall["quelle"], fall["satz_id"], tid) is None:
        return None, [{"field": "_entity", "message": "Kunde bzw. Lieferant des Klaerfalls fehlt.",
                       "severity": "blocking"}]
    return fall, []


@router.post("/{entity_id}/actions/zuordnen", response_model=MaskActionResult,
             summary="Klaerfall einem vorhandenen Geschaeftspartner zuordnen", dependencies=SCHREIBEN["STAMMDATEN"])
async def klaerfall_zuordnen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                             db: Session = Depends(get_db),
                             tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        fall, fehler = _pruefen_basis(session, eid, tid)
        if fehler:
            return fehler
        partner_id = str(payload.get("partner_id") or "").strip()
        if not partner_id:
            return [{"field": "partner_id", "message": "Geschaeftspartner angeben.", "severity": "blocking"}]
        im_mandanten = session.execute(
            text("SELECT 1 FROM domain_crm.business_partners WHERE partner_id = :p AND tenant_id = :tid"),
            {"p": partner_id, "tid": tid}).first()
        if im_mandanten is None:
            return [{"field": "partner_id", "message": "Geschaeftspartner nicht im Mandanten gefunden.",
                     "severity": "blocking"}]
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        fall = _offener_fall(session, eid, tid)
        _erledigen(session, fall, tid, str(payload["partner_id"]).strip())
        return "Klaerfall dem Geschaeftspartner zugeordnet."

    return await run_delegated_mask_action(
        db, action_key="zuordnen", entity_type="partner_klaerfall", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="crm.partner_klaerfall.zugeordnet",
        require_audit_reason=True)


@router.post("/{entity_id}/actions/neuer-partner", response_model=MaskActionResult,
             summary="Klaerfall mit neuem Geschaeftspartner entscheiden", dependencies=SCHREIBEN["STAMMDATEN"])
async def klaerfall_neuer_partner(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                  db: Session = Depends(get_db),
                                  tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        return _pruefen_basis(session, eid, tid)[1]

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        from app.services.business_partner_service import BusinessPartnerService

        fall = _offener_fall(session, eid, tid)
        satz = _satz(session, fall["quelle"], fall["satz_id"], tid)
        partner_id = BusinessPartnerService(session, tid).partner_fuer_rolle(
            fall["quelle"], name=satz["name"] or "", vat_id=satz["ust"], neu_erzwingen=True)
        _erledigen(session, fall, tid, partner_id)
        return "Klaerfall mit neuem Geschaeftspartner entschieden."

    return await run_delegated_mask_action(
        db, action_key="neuer-partner", entity_type="partner_klaerfall", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type="crm.partner_klaerfall.neuer_partner",
        require_audit_reason=True)
