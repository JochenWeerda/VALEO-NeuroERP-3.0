"""Hinweisgebersystem — Meldung, Statusabfrage, Bearbeitung.

Vertraulichkeit ist hier keine Bequemlichkeit, sondern Pflicht: Die
EU-Hinweisgeberrichtlinie (Art. 16) schuetzt die Identitaet des Meldenden und
den Inhalt der Meldung. Drei Dinge folgen daraus, und alle drei fehlten:

1. **Jede Abfrage nennt den Mandanten.** Zuvor listete ``GET /reports`` alle
   Meldungen aller Mandanten, weil die Tabelle zur Laufzeit ohne ``tenant_id``
   angelegt worden war. Schon Existenz, Kategorie und Schwere einer fremden
   Meldung gehoeren nicht in eine Liste.
2. **Die Tabelle kommt aus einer Migration**
   (``whistleblower_eine_tabelle_20260930``), nicht aus einem
   ``CREATE TABLE IF NOT EXISTS`` in diesem Modul. Zuvor entschied die
   Aufrufreihenfolge ueber die Form, und der zweite Endpunkt
   (``compliance_whistleblower_lksg.py``) bekam dauerhaft 503.
3. **Die Notiz wird als JSON gebaut, nicht als Text zusammengesetzt.** Zuvor
   stand sie in einem f-String; ein Anfuehrungszeichen in der Notiz zerlegte
   die Struktur.

Was hier **nicht** geschieht: verschluesseln. Die Spalte hiess
``description_encrypted`` und bekam Klartext — ein Name, der Verschluesselung
verspricht, ist schlechter als einer, der es nicht tut. Sie heisst jetzt
``description``. Eine echte Verschluesselung braucht eine
Schluesselverwaltung und ist eine Entscheidung des Hauses, keine stille
Umbenennung.
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema, StatusResponse
from app.api.v1.schemas.compliance_whistleblower_schemas import ComplianceWhistleblowerOut


# Eigenes Praefix, und zwar aus einem Grund: Ohne Praefix landeten diese
# Routen unter /api/v1/reports — im selben Namensraum wie die
# Verkaufsauswertungen (/api/v1/reports/sales-performance und andere). Ein
# GET /api/v1/reports lieferte damit Hinweisgebermeldungen, wo jemand eine
# Auswertung erwartete. Kein Aufrufer im Repo benutzte die alten Pfade.
#
# Nicht /compliance/whistleblower: Dort liegen bereits die LkSG-Routen
# (compliance_whistleblower_lksg.py), die dieselbe Tabelle bedienen. Ob die
# beiden Wege zusammengelegt gehoeren, ist eine Produktfrage — siehe
# docs/quality-assurance/whistleblower-eine-tabelle-2026-09-30.md.
router = APIRouter(prefix="/compliance/hinweisgeber")

_TABLE = "domain_compliance.whistleblower_reports"

#: Wortlaut fuer den Fall, dass die Migration nicht gelaufen ist. Eine leere
#: Liste waere hier die schlechteste Antwort: Sie sagt „keine Meldungen", wo
#: „nicht nachsehbar" gilt.
_FEHLT = (
    "Tabelle domain_compliance.whistleblower_reports fehlt — Migration "
    "whistleblower_eine_tabelle_20260930 ausfuehren."
)


class ReportIn(BaseModel):
    category: str  # BETRUG/BESTECHUNG/DISKRIMINIERUNG/SICHERHEIT/DATENSCHUTZ/SONSTIGE
    description: str
    severity: str = "MITTEL"


class NoteIn(BaseModel):
    note: str
    new_status: Optional[str] = None


@router.post("/reports", status_code=201, summary="Report einreichen",
    response_model=ComplianceWhistleblowerOut
)
async def submit_report(
    payload: ReportIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    report_id = str(uuid4())
    token = secrets.token_urlsafe(9)[:12].upper()
    try:
        db.execute(
            text(
                f"INSERT INTO {_TABLE} "  # nosec B608
                "(id, tenant_id, report_token, category, description, severity) "
                "VALUES (:id, :tid, :token, :cat, :desc, :sev)"
            ),
            {"id": report_id, "tid": tenant_id, "token": token,
             "cat": payload.category, "desc": payload.description,
             "sev": payload.severity},
        )
        db.commit()
    except Exception as fehler:
        db.rollback()
        raise HTTPException(status_code=503, detail=_FEHLT) from fehler
    return {
        "token": token,
        "message": "Ihr Hinweis wurde vertraulich erfasst. Bewahren Sie den Token zur Rückmeldung auf.",
    }


@router.get("/reports/status/{token}", summary="Status report",
    response_model=ComplianceWhistleblowerOut
)
async def report_status(
    token: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        zeile = db.execute(
            text(
                f"SELECT status, created_at FROM {_TABLE} "  # nosec B608
                "WHERE report_token = :token AND tenant_id = :tid"
            ),
            {"token": token, "tid": tenant_id},
        ).fetchone()
    except Exception as fehler:
        raise HTTPException(status_code=503, detail=_FEHLT) from fehler
    if not zeile:
        # Bewusst dieselbe Antwort fuer „gibt es nicht" und „gehoert einem
        # anderen Mandanten": Der Unterschied waere selbst eine Auskunft.
        raise HTTPException(status_code=404, detail="Kein Hinweis zu diesem Token")
    return {"status": zeile[0], "submitted_at": zeile[1]}


@router.get("/reports", summary="Reports auflisten",
    response_model=list[ComplianceWhistleblowerOut]
)
async def list_reports(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        zeilen = db.execute(
            text(
                f"SELECT id, category, severity, status, created_at FROM {_TABLE} "  # nosec B608
                "WHERE tenant_id = :tid ORDER BY created_at DESC"
            ),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as fehler:
        raise HTTPException(status_code=503, detail=_FEHLT) from fehler
    return [dict(zeile._mapping) for zeile in zeilen]


@router.patch("/reports/{report_id}/update", summary="Report aktualisieren",
    response_model=ComplianceWhistleblowerOut
)
async def update_report(
    report_id: str,
    payload: NoteIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    # Die Notiz wird als JSON erzeugt, nicht als Text zusammengesetzt. Zuvor
    # stand sie in einem f-String: Ein Anfuehrungszeichen in der Notiz zerlegte
    # die Struktur, und ein Hinweisgeberformular ist die letzte Stelle, an der
    # man auf wohlgeformte Eingaben hoffen sollte.
    notiz = json.dumps([{
        "note": payload.note,
        "ts": datetime.now(timezone.utc).isoformat(),
    }])
    try:
        if payload.new_status:
            ergebnis = db.execute(
                text(
                    f"UPDATE {_TABLE} SET status = :st, updated_at = NOW() "  # nosec B608
                    "WHERE id = :id AND tenant_id = :tid"
                ),
                {"st": payload.new_status, "id": report_id, "tid": tenant_id},
            )
            if ergebnis.rowcount == 0:
                db.rollback()
                raise HTTPException(status_code=404, detail="Kein Hinweis mit dieser Kennung")
        ergebnis = db.execute(
            text(
                f"UPDATE {_TABLE} "  # nosec B608
                "SET notes = notes || CAST(:note AS jsonb), updated_at = NOW() "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"note": notiz, "id": report_id, "tid": tenant_id},
        )
        if ergebnis.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=404, detail="Kein Hinweis mit dieser Kennung")
        db.commit()
    except HTTPException:
        raise
    except Exception as fehler:
        db.rollback()
        raise HTTPException(status_code=503, detail=_FEHLT) from fehler
    return {"updated": True}
