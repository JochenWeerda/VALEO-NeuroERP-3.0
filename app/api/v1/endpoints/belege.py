"""Lesender Belegweg: jeder Beleg in der Form des Belegvertrags (BELEG-011).

Die Belegmaske, ein MCP-Werkzeug und jede andere Stelle lesen Belege hier — nicht aus dem Speicher der Domaene.
Heute liefert DocFlow; weitere belegfuehrende Domaenen haengen einen eigenen Adapter ein.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.beleg_roles import darf, verlange
from app.auth.deps import get_current_user
from app.core.belegvertrag import BELEGARTEN, Beleg
from app.core.screen_definitions_beleg import zustandsfeld
from app.core.database import get_db
from app.core.mask_screen_summary_common import build_tab_page
from app.core.tenant import get_tenant_id
from app.services import docflow_belegaktionen
from app.services.docflow_belegadapter import lies_beleg
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action
from app.services.docflow_service import DocflowService
from app.api.v1.schemas.base import TypedObjectOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router = APIRouter()


@router.get("/{belegart}/partner-auswahl", response_model=TypedObjectOut, summary="Mandantengebundene Partnerauswahl fuer Belegentwuerfe")
def beleg_partner_auswahl(
    belegart: str, q: str = Query('', max_length=120), limit: int = Query(25, ge=1, le=50),
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    if belegart not in BELEGARTEN:
        raise HTTPException(404, 'Belegvariante nicht gefunden')
    verlange(nutzer, 'bearbeiten', belegart)
    from app.services.docflow_creation_context import search_partners
    return {'items': search_partners(db, tenant_id, belegart, q.strip(), limit)}


def _lies(belegart: str, beleg_id: str, tenant_id: str, db: Session, nutzer: Any) -> Beleg:
    return beleg_lesen(belegart, beleg_id, tenant_id, db, nutzer)


@router.get("/{belegart}/{beleg_id}/kopf", response_model=TypedObjectOut, summary="Belegkopf fuer die Belegmaske")
def beleg_kopf(
    belegart: str,
    beleg_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Der Kopf des Belegs als flache Felder — dieselben Daten und Rechte wie der Belegvertrag."""
    beleg = _lies(belegart, beleg_id, tenant_id, db, nutzer)
    kopf: dict[str, Any] = {
        "beleg_id": beleg.beleg_id, "belegart": beleg.belegart, "beleg_nr": beleg.beleg_nr, "status": beleg.status,
        "belegdatum": beleg.belegdatum.isoformat(), "version": beleg.version,
        "partner_nummer": beleg.partner.nummer if beleg.partner else None,
        "partner_name": beleg.partner.name if beleg.partner else None,
        "preise_sichtbar": beleg.preise_sichtbar,
        "buchungsstand": beleg.buchung.stand, "buchungsgrund": beleg.buchung.grund,
        "aktionen": [a.model_dump(mode="json") for a in beleg.aktionen],
        # Was gerade nicht geht, und warum — fuer den Menschen an der Maske.
        # Dazu, was beim Ausfuehren im Pruefkorb vermerkt wird (``hinweis`` an einer erlaubten Aktion).
        "aktionshinweis": "\n".join(
            f"{a.bezeichnung}: {a.hinweis if a.erlaubt else a.grund}"
            for a in beleg.aktionen if (a.hinweis if a.erlaubt else a.grund)
        ) or None,
    }
    # Je Aktion ein Feld, an dem der Knopf der Maske haengt (``enabledWhen``). Was der Beleg nicht anbietet, fehlt.
    for aktion in beleg.aktionen:
        kopf[zustandsfeld(aktion.key)] = aktion.erlaubt
    if beleg.summen is not None:
        kopf.update(waehrung=beleg.waehrung, netto=str(beleg.summen.netto), steuer=str(beleg.summen.steuer),
                    brutto=str(beleg.summen.brutto))
    return kopf


@router.get("/{belegart}/{beleg_id}/tabs/{reiter}", response_model=TypedObjectOut, summary="Reiter der Belegmaske")
def beleg_reiter(
    belegart: str,
    beleg_id: str,
    reiter: str,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: str | None = Query(None),
    sort: str | None = Query(None),
    sort_dir: str | None = Query(None, pattern="^(asc|desc)$"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Positionen, Belegkette, Dokumente oder Verlauf als Seite — aus dem Belegvertrag, nicht aus Tabellen."""
    if reiter not in ("positionen", "kette", "dokumente", "historie"):
        raise HTTPException(status_code=404, detail="Reiter nicht bekannt")
    beleg = _lies(belegart, beleg_id, tenant_id, db, nutzer)
    zeilen = [z.model_dump(mode="json", exclude={"bausteine"}) for z in getattr(beleg, reiter)]
    if reiter == "kette":
        for z in zeilen:
            z["bezeichnung"] = BELEGARTEN[z["belegart"]].bezeichnung if z["belegart"] in BELEGARTEN else z["belegart"]
            z["richtung"] = "Vorgänger" if z["richtung"] == "vorgaenger" else "Nachfolger"
    return build_tab_page(tab_key=reiter, table_key=reiter, items=zeilen, page=page, limit=limit, q=q,
                          sort=sort, sort_dir=sort_dir)


@router.post("/{belegart}/{beleg_id}/actions/{aktion}", response_model=MaskActionResult,
             summary="Aktion der Belegmaske ausfuehren (Masken-CommandEndpoint)", dependencies=SCHREIBEN["BELEGE"])
async def beleg_aktion(
    belegart: str,
    beleg_id: str,
    aktion: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> MaskActionResult:
    """Buchen, Stornieren, Freigeben, Folgebeleg erstellen, Freigabe anfragen und entscheiden.

    ``aktion`` ist der Schluessel aus ``aktionen`` des Belegvertrags. Der Trockenlauf nennt den Sperrgrund, ohne zu
    schreiben; ausgefuehrt wird das eine Fachkommando von DocFlow bzw. der Approval Engine.
    """
    if belegart not in BELEGARTEN:
        raise HTTPException(status_code=404, detail="Belegart nicht bekannt")
    verlange(nutzer, "lesen", belegart)

    async def pruefe(pruef_db: Session, eingaben: dict[str, Any], entity_id: str, tid: str) -> list[dict[str, Any]]:
        return docflow_belegaktionen.pruefe(pruef_db, tid, belegart, entity_id, aktion, nutzer, eingaben)

    async def fuehre_aus(schreib_db: Session, eingaben: dict[str, Any], entity_id: str, tid: str) -> str:
        return docflow_belegaktionen.fuehre_aus(schreib_db, tid, belegart, entity_id, aktion, nutzer, eingaben)

    return await run_delegated_mask_action(
        db, action_key=aktion, entity_type=f"beleg_{belegart}", entity_id=beleg_id, tenant_id=tenant_id,
        body=body, check_fn=pruefe, delegate_fn=fuehre_aus, outbox_event_type="beleg.aktion.ausgefuehrt",
    )


@router.get("/{belegart}/{beleg_id}", response_model=Beleg, summary="Beleg in Vertragsform lesen")
def beleg_lesen(
    belegart: str,
    beleg_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> Beleg:
    """Kopf, Partner, Positionen, Summen, Buchungsstand, Belegkette, Historie und Aktionen.

    Ohne Preisrecht kommen weder Preisfelder noch Summen; Aktionen ohne Recht sind gesperrt.
    """
    if belegart not in BELEGARTEN:
        raise HTTPException(status_code=404, detail="Belegart nicht bekannt")
    # Vor dem ersten Datenbankzugriff: Wer die Belegart nicht lesen darf, erfaehrt auch nicht, ob es den Beleg gibt.
    verlange(nutzer, "lesen", belegart)
    leser = str(nutzer.get("sub") or "") if isinstance(nutzer, dict) else None
    beleg = lies_beleg(DocflowService(db, tenant_id), beleg_id, lambda recht, art: darf(nutzer, recht, art), leser)
    # Ein Beleg anderer Art unter dieser Adresse ist nicht dieser Beleg.
    if beleg is None or beleg.belegart != belegart:
        raise HTTPException(status_code=404, detail="Beleg nicht gefunden")
    return beleg
