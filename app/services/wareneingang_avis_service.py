"""Wareneingang aus dem Anlieferavis — DocFlow-Bestellung beliefert, Ware im Lager (BELEG-052 Phase 3b).

Bis zum 10.11.2026 fuehrte das Avis zur Bestellung im Altspeicher (``domain_einkauf.bestellungen``) und buchte den
Zugang an ihr vorbei. Jetzt ist DocFlow der einzige Belegspeicher. In **einem** Commit:

* Das Avis fuehrt ueber ``bestell_nr`` zur DocFlow-Bestellung (freigegeben oder bestaetigt), beides im Mandanten.
* Aus der Bestellung entsteht der Wareneingang ueber dieselbe Umwandlung wie in der Belegmaske - mit der ganzen
  Restmenge je Position; die Lieferschein-Nr. steht als fremde Referenz im Kopf.
* Der Wareneingang wird eingelagert (``DocflowService.einlagern``): Zugang je Position ins Lager, Beleg abgeschlossen.
* Avis ``ERHALTEN``.

Abgelehnt: fremdes Avis oder Lager, Avis ohne Bestellbezug, nichts mehr offen (kein zweiter Wareneingang), eine
Position ohne Artikel oder mit nicht umrechenbarer Einheit - dann wird gar nichts gebucht.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, ValidationFailedError


class WareneingangAvisError(Exception):
    """Der Wareneingang ist so nicht buchbar; die Nachricht nennt den Grund."""


def _avis_und_bestellung(db: Session, avis_id: str, tenant_id: str) -> tuple[dict, dict]:
    avis = db.execute(
        text("SELECT id, avis_nummer, bestell_nr, status FROM einkauf_anlieferavis "
             "WHERE id = :id AND tenant_id = :tid FOR UPDATE"),
        {"id": avis_id, "tid": tenant_id},
    ).mappings().first()
    if not avis:
        raise WareneingangAvisError("Anlieferavis nicht gefunden.")
    bestellung = db.execute(
        text("SELECT id::text AS id, doc_number AS bestellnummer, status FROM domain_docflow.document_headers "
             "WHERE tenant_id = :tid AND doc_type = 'purchase_order' AND doc_number = :nr AND deleted_at IS NULL"),
        {"nr": avis["bestell_nr"] or "", "tid": tenant_id},
    ).mappings().first()
    if not bestellung:
        raise WareneingangAvisError(
            f"Zum Avis {avis['avis_nummer']} gibt es keine Bestellung {avis['bestell_nr'] or '(ohne Nummer)'}."
        )
    if bestellung["status"] not in ("open", "confirmed"):
        raise WareneingangAvisError(
            f"Bestellung {bestellung['bestellnummer']} ist nicht freigegeben (Stand {bestellung['status']}).")
    return dict(avis), dict(bestellung)


def _restmengen(db: Session, tenant_id: str, bestellung_id: str) -> list[dict[str, Any]]:
    """Positionen der Bestellung mit der noch nicht in einen Wareneingang uebernommenen Menge."""
    from app.services.docflow_service import TRANSITIONS, DocflowService

    svc = DocflowService(db, tenant_id, "wareneingang")
    schon = svc.umgewandelte_mengen(bestellung_id, TRANSITIONS["purchase_order"]["goods_receipt"])
    offen = []
    for pos in svc.fetch_items(bestellung_id):
        rest = Decimal(str(pos.get("quantity") or 0)) - schon.get(str(pos["id"]), Decimal("0"))
        if rest > 0:
            offen.append({**pos, "quantity": rest})
    return offen


def pruefe_wareneingang(db: Session, avis_id: str, tenant_id: str, lager_id: str, lieferschein_nr: str) -> list:
    """Alles, was gegen die Buchung spricht — ohne zu schreiben. Liefert die offenen Positionen."""
    from app.services.docflow_lagerzugang import pruefe_lagerzugang

    if not str(lieferschein_nr or "").strip():
        raise WareneingangAvisError("Lieferschein-Nr. fehlt.")
    _, bestellung = _avis_und_bestellung(db, avis_id, tenant_id)
    offen = _restmengen(db, tenant_id, bestellung["id"])
    if not offen:
        raise WareneingangAvisError(
            f"Bestellung {bestellung['bestellnummer']} hat nichts mehr offen; ein Wareneingang ist schon gebucht."
        )
    try:
        pruefe_lagerzugang(db, tenant_id, offen, lager_id)
    except ValidationFailedError as exc:
        raise WareneingangAvisError(str(exc.detail if hasattr(exc, "detail") else exc)) from exc
    return offen


def buche_wareneingang_aus_avis(
    db: Session, avis_id: str, tenant_id: str, lager_id: str, lieferschein_nr: str, operator: str | None = None,
) -> dict[str, Any]:
    """Bucht den Wareneingang; der Aufrufer committet nicht — dieser Dienst schon."""
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest
    from app.services.docflow_service import DocflowService

    avis, bestellung = _avis_und_bestellung(db, avis_id, tenant_id)
    offen = pruefe_wareneingang(db, avis_id, tenant_id, lager_id, lieferschein_nr)
    lieferschein = lieferschein_nr.strip()
    try:
        # Die Umwandlung committet selbst: auf einen Sicherungspunkt begrenzt, damit Wareneingang, Lagerzugang und
        # Avis-Stand zusammen gelten oder gar nicht.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as kind:
            umwandlung = DocflowService(kind, tenant_id, operator or "wareneingang").convert(
                bestellung["id"], DocflowConvertRequest(
                    target_doc_type="goods_receipt", idempotency_key=f"avis-{avis_id}-{uuid.uuid4().hex}"[:120],
                    quantities_by_source_item_id={str(p["id"]): float(p["quantity"]) for p in offen},
                    created_by=operator))
        wareneingang = str(umwandlung["target_doc_id"])
        db.execute(text(
            "UPDATE domain_docflow.document_headers SET bausteine = COALESCE(bausteine, '{}'::jsonb) || "
            "jsonb_build_object('referenzen', jsonb_build_object('fremde_referenz', CAST(:ls AS text))) "
            "WHERE id = :id AND tenant_id = :tid"), {"ls": lieferschein, "id": wareneingang, "tid": tenant_id})
        svc = DocflowService(db, tenant_id, operator or "wareneingang")
        svc.einlagern(wareneingang, lager_id, f"avis-einlagern-{avis_id}"[:120], None, operator, commit=False)
    except DomainError as exc:
        db.rollback()
        raise WareneingangAvisError(str(getattr(exc, "detail", exc))) from exc
    db.execute(
        text("UPDATE einkauf_anlieferavis SET status = 'ERHALTEN', updated_at = NOW() "
             "WHERE id = :id AND tenant_id = :tid"),
        {"id": avis_id, "tid": tenant_id},
    )
    db.commit()
    return {
        "avis_id": avis_id,
        "bestellung_id": bestellung["id"],
        "bestellnummer": bestellung["bestellnummer"],
        "wareneingang_id": wareneingang,
        "positionen": len(offen),
        "lieferschein_nr": lieferschein,
    }
