"""Kommunikation zu einer Bestellung — wirklich versendet, am fuehrenden Beleg.

Bis zum 08.10.2026 schrieben die Kommunikationswege an ``/purchase-orders`` in
den Dokumentspeicher und fanden nur Altbelege (kanonische Bestellungen: 404).
"E-Mail senden" und "Im Portal veroeffentlichen" setzten ``status: "sent"`` bzw.
``"published"``, ohne etwas zu versenden oder zu veroeffentlichen.

Hier gilt:

* Gespeichert wird in ``domain_einkauf.bestellung_kommunikation`` — dort liest
  auch der Reiter "Kommunikation" der Bestellmaske.
* E-Mail: Versand ueber SMTP (:mod:`app.services.mail_versand`); eingetragen als
  ``versendet`` erst, wenn der Server angenommen hat. Ohne Einrichtung oder bei
  Ablehnung wird nichts als versendet eingetragen.
* Portal: eingetragen als ``veroeffentlicht``; das Lieferantenportal zeigt dem
  Lieferanten genau diese Bestellungen
  (``GET /supplier-portal/lieferanten/{id}/bestellungen``).
* Sonst: ``erfasst`` — eine protokollierte Kommunikation (Telefonat, Brief),
  kein Versand.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.mail_versand import sende_mail


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


def _eintragen(
    db: Session, tenant_id: str, bestellung_id: str, *, kanal: str, status: str,
    empfaenger: Optional[str], betreff: str, nachricht: str, versendet: bool, von: Optional[str],
) -> dict[str, Any]:
    kennung = str(uuid.uuid4())
    db.execute(
        text(
            "INSERT INTO domain_einkauf.bestellung_kommunikation "
            "(id, tenant_id, bestellung_id, kanal, empfaenger, betreff, nachricht, status, versendet_am, erfasst_von) "
            "VALUES (:id, :t, :b, :k, :e, :betreff, :n, :s, CASE WHEN :v THEN NOW() END, :von)"
        ),
        {"id": kennung, "t": tenant_id, "b": bestellung_id, "k": kanal, "e": empfaenger, "betreff": betreff,
         "n": nachricht, "s": status, "v": versendet, "von": von},
    )
    zeile = db.execute(
        text("SELECT * FROM domain_einkauf.bestellung_kommunikation WHERE id = :id"), {"id": kennung}
    ).mappings().one()
    return _aussen(dict(zeile))


def _lieferanten_mail(db: Session, tenant_id: str, bestellung_id: str) -> Optional[str]:
    return db.execute(
        text(
            "SELECT COALESCE(NULLIF(l.email_bestellung, ''), NULLIF(l.email, '')) "
            "FROM domain_einkauf.bestellungen b JOIN domain_einkauf.lieferanten l "
            "  ON l.id::text = b.lieferant_id::text AND l.tenant_id = b.tenant_id "
            "WHERE b.id = :b AND b.tenant_id = :t"
        ),
        {"b": bestellung_id, "t": tenant_id},
    ).scalar()


def erfassen(db: Session, tenant_id: str, beleg: dict[str, Any], payload: dict[str, Any],
             von: Optional[str] = None) -> dict[str, Any]:
    """Eine Kommunikation protokollieren (kein Versand)."""
    return _eintragen(
        db, tenant_id, beleg["id"], kanal=str(payload.get("channel") or "notiz"), status="erfasst",
        empfaenger=payload.get("recipient"), betreff=str(payload.get("subject") or f"Bestellung {beleg['bestellnummer']}"),
        nachricht=str(payload.get("message") or ""), versendet=False, von=von,
    )


def per_mail_senden(db: Session, tenant_id: str, beleg: dict[str, Any], payload: dict[str, Any],
                    von: Optional[str] = None) -> dict[str, Any]:
    """Versendet ueber SMTP und traegt erst danach ein. Wirft bei jedem Scheitern."""
    empfaenger = (payload.get("recipient") or "").strip() or _lieferanten_mail(db, tenant_id, beleg["id"])
    if not empfaenger:
        raise ValueError("Kein Empfaenger: weder angegeben noch beim Lieferanten hinterlegt.")
    betreff = str(payload.get("subject") or f"Bestellung {beleg['bestellnummer']}")
    nachricht = str(payload.get("message") or "")
    sende_mail(empfaenger, betreff, nachricht)
    return _eintragen(db, tenant_id, beleg["id"], kanal="email", status="versendet", empfaenger=empfaenger,
                      betreff=betreff, nachricht=nachricht, versendet=True, von=von)


def im_portal_veroeffentlichen(db: Session, tenant_id: str, beleg: dict[str, Any], payload: dict[str, Any],
                               von: Optional[str] = None) -> dict[str, Any]:
    """Macht die Bestellung im Lieferantenportal sichtbar."""
    if str(beleg.get("status") or "").lower() in ("entwurf", "storniert"):
        raise ValueError(f"Bestellung {beleg['bestellnummer']} ist {beleg['status']} und wird nicht veroeffentlicht.")
    return _eintragen(
        db, tenant_id, beleg["id"], kanal="portal", status="veroeffentlicht", empfaenger=None,
        betreff=str(payload.get("subject") or f"Bestellung {beleg['bestellnummer']}"),
        nachricht=str(payload.get("message") or ""), versendet=True, von=von,
    )


def veroeffentlichte_fuer_lieferant(db: Session, tenant_id: str, lieferant_id: str) -> list[dict[str, Any]]:
    """Die Bestellungen, die einem Lieferanten im Portal veroeffentlicht wurden."""
    zeilen = db.execute(
        text(
            "SELECT b.id, b.bestellnummer, b.bestelldatum, b.lieferdatum_wunsch, b.status, b.brutto_summe, "
            "       max(k.versendet_am) AS veroeffentlicht_am "
            "FROM domain_einkauf.bestellungen b "
            "JOIN domain_einkauf.bestellung_kommunikation k "
            "  ON k.bestellung_id = b.id::text AND k.tenant_id = b.tenant_id "
            " AND k.kanal = 'portal' AND k.status = 'veroeffentlicht' "
            "WHERE b.tenant_id = :t AND b.lieferant_id::text = :l "
            "GROUP BY b.id ORDER BY veroeffentlicht_am DESC LIMIT 200"
        ),
        {"t": tenant_id, "l": lieferant_id},
    ).mappings().all()
    return [
        {
            "bestellung_id": str(z["id"]),
            "bestellnummer": z["bestellnummer"],
            "bestelldatum": z["bestelldatum"].isoformat() if z["bestelldatum"] else None,
            "liefertermin": z["lieferdatum_wunsch"].isoformat() if z["lieferdatum_wunsch"] else None,
            "status": z["status"],
            "betrag_brutto": float(z["brutto_summe"] or 0),
            "veroeffentlicht_am": z["veroeffentlicht_am"].isoformat() if z["veroeffentlicht_am"] else None,
        }
        for z in zeilen
    ]
