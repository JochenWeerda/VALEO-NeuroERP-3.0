"""Kommunikation zu einer Bestellung (Reiter "Kommunikation") - nur noch lesend.

Die Eintraege stehen in ``domain_einkauf.bestellung_kommunikation`` und verweisen auf die DocFlow-Bestellung
(BELEG-052 S3). Versendet wird an der Belegmaske (``/belege/{belegart}/{id}/actions/versenden``, E-Mail ueber das
Einkaufspostfach). Die frueheren Wege Notiz/E-Mail/Portal dieses Dienstes hingen an der Altbestellung und hatten
seit Phase 3b keinen Aufrufer mehr. Das Lieferantenportal zeigt weiter, was dort veroeffentlicht wurde.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session



def liste(db: Session, tenant_id: str, bestellung_id: str) -> list[dict[str, Any]]:
    zeilen = db.execute(
        text(
            "SELECT id, kanal, empfaenger, betreff, nachricht, status, versendet_am, erfasst_am, erfasst_von "
            "FROM domain_einkauf.bestellung_kommunikation "
            "WHERE tenant_id = :t AND bestellung_id = :b ORDER BY erfasst_am DESC LIMIT 500"
        ),
        {"t": tenant_id, "b": bestellung_id},
    ).mappings().all()
    return [_aussen(dict(z)) for z in zeilen]


def _aussen(z: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": z["id"],
        "channel": z["kanal"],
        "recipient": z["empfaenger"],
        "subject": z["betreff"],
        "message": z["nachricht"] or "",
        "status": z["status"],
        "sentAt": z["versendet_am"].isoformat() if z.get("versendet_am") else None,
        "createdAt": z["erfasst_am"].isoformat() if z.get("erfasst_am") else None,
        "createdBy": z.get("erfasst_von"),
    }


def veroeffentlichte_fuer_lieferant(db: Session, tenant_id: str, lieferant_id: str) -> list[dict[str, Any]]:
    """Die Bestellungen, die einem Lieferanten im Portal veroeffentlicht wurden."""
    zeilen = db.execute(
        text(
            "SELECT b.id, b.doc_number AS bestellnummer, b.document_date AS bestelldatum, "
            "       b.bausteine #>> '{lieferung,liefertermin}' AS lieferdatum_wunsch, b.status, "
            "       b.total_gross AS brutto_summe, max(k.versendet_am) AS veroeffentlicht_am "
            "FROM domain_docflow.document_headers b "
            "JOIN domain_einkauf.bestellung_kommunikation k "
            "  ON k.bestellung_id = b.id::text AND k.tenant_id = b.tenant_id "
            " AND k.kanal = 'portal' AND k.status = 'veroeffentlicht' "
            "WHERE b.tenant_id = :t AND b.doc_type = 'purchase_order' AND b.deleted_at IS NULL "
            "  AND b.supplier_id = :l "
            "GROUP BY b.id ORDER BY veroeffentlicht_am DESC LIMIT 200"
        ),
        {"t": tenant_id, "l": lieferant_id},
    ).mappings().all()
    return [
        {
            "bestellung_id": str(z["id"]),
            "bestellnummer": z["bestellnummer"],
            "bestelldatum": z["bestelldatum"].isoformat() if z["bestelldatum"] else None,
            "liefertermin": z["lieferdatum_wunsch"],
            "status": z["status"],
            "betrag_brutto": float(z["brutto_summe"] or 0),
            "veroeffentlicht_am": z["veroeffentlicht_am"].isoformat() if z["veroeffentlicht_am"] else None,
        }
        for z in zeilen
    ]
