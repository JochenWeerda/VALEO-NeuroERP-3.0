"""Frachtbrief als Transportbeleg der Sendung, nicht als Lieferschein.

Die Verladung liefert Fahrzeug, Ware, Menge und Orte. Daraus wird eine Sendung.
Dieser Dienst schreibt nur die Transportansicht. Der Lieferschein bleibt der
Warenbeleg und steht lediglich als Referenz am Frachtbrief.
Eine Ausgangswägung schreibt die endgültige Menge nach.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domains.logistik.sendung import frachtbrief_sicht, sendung_aus_verladung

_BEREIT_STATUS = "verladen"


def fehlende_angaben(verladung: Any) -> list[str]:
    """Pflicht des Transportbelegs. Leer heißt: der Frachtbrief darf entstehen."""
    fehlend: list[str] = []
    if str(getattr(verladung, "status", "") or "") != _BEREIT_STATUS:
        fehlend.append("verladung")
    if not str(getattr(verladung, "kennzeichen", "") or "").strip():
        fehlend.append("fahrzeug")
    if not str(getattr(verladung, "artikel", "") or "").strip():
        fehlend.append("ware")
    menge = getattr(verladung, "menge", None)
    if menge is None or Decimal(str(menge)) <= 0:
        fehlend.append("menge")
    if not str(getattr(verladung, "ladeort", "") or "").strip():
        fehlend.append("uebernahmeort")
    empfaenger = str(getattr(verladung, "kunde", "") or "").strip() or str(
        getattr(verladung, "zielort", "") or ""
    ).strip()
    if not empfaenger:
        fehlend.append("empfaenger")
    return fehlend


def _belegnummer(verladung_id: str) -> str:
    return f"FB-{verladung_id}"[:60]


def _datum(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.today()


def generate_from_verladung(db: Session, verladung: Any, tenant_id: str) -> str | None:
    """Erzeugt höchstens einen Frachtbrief je Verladung. Nicht bereit → None."""
    sendung = sendung_aus_verladung(verladung)
    if sendung is None:
        return None
    transport = frachtbrief_sicht(sendung)
    nummer = _belegnummer(str(verladung.id))
    vorhanden = db.execute(
        text(
            "SELECT id FROM domain_logistics.frachtbriefe "
            "WHERE tenant_id = :tenant_id AND nummer = :nummer"
        ),
        {"tenant_id": tenant_id, "nummer": nummer},
    ).first()
    if vorhanden:
        return str(vorhanden[0])

    fb_id = str(uuid.uuid4())
    db.execute(
        text(
            "INSERT INTO domain_logistics.frachtbriefe"
            " (id, tenant_id, nummer, kennzeichen, artikel, menge, absender, empfaenger,"
            "  datum, status, lieferschein_ref)"
            " VALUES (:id, :tenant_id, :nummer, :kennzeichen, :artikel, :menge, :absender,"
            "         :empfaenger, :datum, 'erstellt', :lieferschein_ref)"
        ),
        {
            "id": fb_id,
            "tenant_id": tenant_id,
            "nummer": nummer,
            "kennzeichen": transport.kennzeichen[:20],
            "artikel": transport.artikel[:120],
            "menge": transport.menge,
            "absender": transport.absender[:120],
            "empfaenger": transport.empfaenger[:120],
            "datum": _datum(getattr(verladung, "datum", None)),
            "lieferschein_ref": (transport.lieferschein_nr[:60] if transport.lieferschein_nr else None),
        },
    )
    return fb_id


def finalize_menge_from_outbound_weighing(
    db: Session,
    *,
    tenant_id: str,
    kennzeichen: str | None,
    netto_kg: float | None,
    zielschein_typ: str | None,
) -> None:
    """Schüttgut: die Ausgangswägung ersetzt die Lademenge am offenen Frachtbrief."""
    if (zielschein_typ or "").upper() != "VL":
        return
    plate = (kennzeichen or "").strip()
    if not plate or netto_kg is None:
        return
    menge_t = (Decimal(str(netto_kg)) / Decimal("1000")).quantize(Decimal("0.001"))
    db.execute(
        text(
            "UPDATE domain_logistics.frachtbriefe SET menge = :menge, updated_at = NOW()"
            " WHERE id = ("
            "   SELECT id FROM domain_logistics.frachtbriefe"
            "   WHERE tenant_id = :tenant_id AND kennzeichen = :kennzeichen AND status = 'erstellt'"
            "   ORDER BY created_at DESC LIMIT 1"
            " )"
        ),
        {"menge": menge_t, "tenant_id": tenant_id, "kennzeichen": plate[:20]},
    )
