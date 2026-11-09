"""Beleg versenden: der Beleg als PDF per E-Mail an seinen Partner (BELEG-052 Stufe 2b, 09.11.2026).

Bisher konnte nur die Bestellung des alten Einkaufsspeichers versandt werden (``/einkauf/bestellungen/{id}/actions/
versenden``). Seit DocFlow der einzige Belegspeicher ist, versendet jede Belegvariante: Angebot, Auftrag, Lieferschein,
Rechnung, Gutschrift, Bestellung, Wareneingang, Eingangsrechnung, Einkaufsgutschrift. Der Weg:

* Pruefung in jedem Modus: Beleg da, Stand versendbar (nicht Entwurf, nicht storniert), Empfaengeradresse vorhanden.
* Versand ueber den einen Mailweg ``mail_versand.sende_mail`` (Postfach des Mandanten je Verwendung ``verkauf`` bzw.
  ``einkauf``, Freigaben des Postfachs); das PDF ist dasselbe wie beim Belegdruck.
* Kein Erfolg ohne Versand: Scheitert die Mail, scheitert die Aktion.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.beleg_roles import verlange
from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.belegvertrag import BELEGARTEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=["belege", "mask-actions"])

VERSENDBAR = frozenset({"open", "released", "posted"})


def partner_email(db: Session, tenant_id: str, rolle: str, kennung: Optional[str]) -> Optional[str]:
    """E-Mail des Partners aus dem Stamm (Lieferant: Bestelladresse vor allgemeiner Adresse)."""
    if not kennung:
        return None
    if rolle == "lieferant":
        sql = ("SELECT COALESCE(NULLIF(email_bestellung, ''), NULLIF(email, '')) FROM domain_einkauf.lieferanten "
               "WHERE tenant_id = :t AND (id::text = :p OR lieferantennummer = :p) LIMIT 1")
    else:
        sql = ("SELECT COALESCE(NULLIF(c.email, ''), NULLIF(bp.email, '')) FROM domain_crm.customers c "
               "LEFT JOIN domain_crm.business_partners bp ON bp.partner_id = c.business_partner_id "
               "AND bp.tenant_id = c.tenant_id "
               "WHERE c.tenant_id = :t AND (c.id::text = :p OR c.customer_number = :p) LIMIT 1")
    with db.begin_nested():
        return db.execute(text(sql), {"t": tenant_id, "p": str(kennung)}).scalar()


@router.post("/belege/{belegart}/{entity_id}/actions/versenden", response_model=MaskActionResult,
             summary="Beleg als PDF per E-Mail an den Partner senden", dependencies=SCHREIBEN["BELEGE"])
async def beleg_versenden(belegart: str, entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                          nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    if belegart not in BELEGARTEN:
        raise HTTPException(status_code=404, detail="Belegart nicht bekannt")
    verlange(nutzer, "ausstellen", belegart)
    variante = BELEGARTEN[belegart]

    def _beleg(session: Session, eid: str, tid: str):
        from app.api.v1.endpoints.belege import beleg_lesen

        return beleg_lesen(belegart, eid, tid, session, nutzer)

    def _empfaenger(session: Session, beleg, payload: dict, tid: str) -> Optional[str]:
        eigen = str(payload.get("empfaenger") or "").strip()
        if eigen:
            return eigen
        return partner_email(session, tid, variante.partnerrolle, beleg.partner.nummer if beleg.partner else None)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        try:
            beleg = _beleg(session, eid, tid)
        except HTTPException as exc:
            return [{"field": "_entity", "message": str(exc.detail), "severity": "blocking"}]
        if beleg.status not in VERSENDBAR:
            return [{"field": "_entity", "message": f"Beleg im Stand {beleg.status} wird nicht versandt.",
                     "severity": "blocking"}]
        empfaenger = _empfaenger(session, beleg, payload, tid)
        if not empfaenger or "@" not in empfaenger:
            return [{"field": "empfaenger", "message": "Keine E-Mail-Adresse beim Partner hinterlegt.",
                     "severity": "blocking"}]
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        from app.services.beleg_druck import beleg_pdf
        from app.services.mail_versand import sende_mail

        beleg = _beleg(session, eid, tid)
        empfaenger = _empfaenger(session, beleg, payload, tid) or ""
        titel = f"{variante.bezeichnung} {beleg.beleg_nr}"
        nachricht = str(payload.get("nachricht") or "").strip() or f"Anbei {titel}."
        sende_mail(empfaenger, titel, nachricht, db=session, tenant_id=tid,
                   verwendung="einkauf" if variante.richtung == "einkauf" else "verkauf", nutzer=nutzer,
                   anhaenge=[(f"{belegart}_{beleg.beleg_nr}.pdf".replace("/", "-"), beleg_pdf(beleg),
                              "application/pdf")])
        return f"{titel} an {empfaenger} versandt."

    return await run_delegated_mask_action(
        db, action_key="versenden", entity_type=f"beleg:{belegart}", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type=f"beleg.{belegart}.versandt")
