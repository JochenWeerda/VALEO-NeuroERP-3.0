"""Lesender Belegweg: jeder Beleg in der Form des Belegvertrags (BELEG-011).

Die Belegmaske, ein MCP-Werkzeug und jede andere Stelle lesen Belege hier — nicht aus dem Speicher der Domaene.
Heute liefert DocFlow; weitere belegfuehrende Domaenen haengen einen eigenen Adapter ein.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.beleg_roles import darf, verlange
from app.auth.deps import get_current_user
from app.core.belegvertrag import BELEGARTEN, Beleg
from app.core.database import get_db
from app.core.mask_screen_summary_common import build_tab_page
from app.core.tenant import get_tenant_id
from app.services.docflow_belegadapter import lies_beleg
from app.services.docflow_service import DocflowService

router = APIRouter()


def _lies(belegart: str, beleg_id: str, tenant_id: str, db: Session, nutzer: Any) -> Beleg:
    return beleg_lesen(belegart, beleg_id, tenant_id, db, nutzer)


@router.get("/{belegart}/{beleg_id}/kopf", response_model=dict[str, Any], summary="Belegkopf fuer die Belegmaske")
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
    }
    if beleg.summen is not None:
        kopf.update(waehrung=beleg.waehrung, netto=str(beleg.summen.netto), steuer=str(beleg.summen.steuer),
                    brutto=str(beleg.summen.brutto))
    return kopf


@router.get("/{belegart}/{beleg_id}/tabs/{reiter}", response_model=dict[str, Any], summary="Reiter der Belegmaske")
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
