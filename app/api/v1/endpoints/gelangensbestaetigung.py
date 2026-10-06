"""
Gelangensbestätigung API — §17a UStDV
Steuerfreie innergemeinschaftliche Lieferungen (EU).
Nachweis des Gelangens des Liefergegenstandes in das übrige Gemeinschaftsgebiet.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import Body, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, IDResponse


router = APIRouter(prefix="/gelangensbestaetigung", tags=["Gelangensbestätigung", "UStDV"])

MIGRATION_HINT = (
    "Tabelle domain_compliance.gelangensbestaetigung fehlt — "
    "bitte Alembic-Migration ausführen: alembic upgrade head"
)

ERINNERUNG_TAGE = 90  # §17a UStDV: Nachweis innerhalb von 3 Monaten


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class GelangensbestaetigungCreate(BaseModel):
    lieferschein_nr: str
    rechnung_nr: str
    kunde_nr: str
    bestimmungsland_code: str = Field(..., min_length=2, max_length=2, description="EU-Mitgliedstaat ISO 3166-1")
    warenwert_eur: float = Field(..., gt=0)
    versanddatum: date
    empfaenger_name: str
    empfaenger_ust_id_nr: str


class GelangensbestaetigungOut(BaseModel):
    """Ein Nachweis, wie ihn die Liste zurueckgibt.

    ``rechnung_nr`` und ``empfaenger_ust_id_nr`` sind **optional**: Beide duerfen
    in der Datenbank fehlen, und ein Pflichtfeld hier haette jede Liste mit einer
    solchen Zeile in einen 500er verwandelt. Aufgefallen ist das erst, als es die
    Tabelle gab — vorher antwortete jeder Weg 503.
    """

    id: str
    lieferschein_nr: str
    rechnung_nr: Optional[str] = None
    kunde_nr: str
    bestimmungsland_code: str
    warenwert_eur: float
    versanddatum: str
    empfaenger_name: str
    empfaenger_ust_id_nr: Optional[str] = None
    status: str  # AUSSTEHEND | ERHALTEN | ABGELAUFEN
    token: str
    erinnerung_am: Optional[str] = None
    erhalten_am: Optional[str] = None


class GelangensbestaetigungCreateOut(BaseModel):
    """Was das Anlegen zurueckgibt.

    Vorher stand hier ``GelangensbestaetigungOut`` — ein Modell mit zehn
    Pflichtfeldern, von denen das Anlegen vier liefert. Der Weg konnte deshalb
    **nie** 201 antworten; sichtbar wurde es nicht, weil die fehlende Tabelle
    vorher 503 ergab.
    """

    id: str
    token: str
    erinnerung_am: str
    status: str


class GelangensbestaetigungFaelligOut(BaseModel):
    """Was die Faelligkeitsliste zurueckgibt — ohne Status und USt-IdNr.

    Dieselbe Falle wie beim Anlegen: Die Abfrage waehlt zehn Felder, das alte
    Modell verlangte dreizehn.
    """

    id: str
    lieferschein_nr: str
    rechnung_nr: Optional[str] = None
    kunde_nr: str
    empfaenger_name: str
    bestimmungsland_code: str
    warenwert_eur: float
    versanddatum: str
    token: str
    erinnerung_am: Optional[str] = None


class MahnungOut(BaseModel):
    """Was das Erinnern zurueckgibt.

    Bis zum 06.10.2026 stand hier ``erinnerung_gesendet: True`` — neben dem
    Kommentar „Stub: In production this would send email/fax". Es wurde nichts
    versendet. Die Erinnerung ist Teil der Nachweiskette nach § 17a UStDV; eine
    Antwort „gesendet" heisst, dass niemand mehr nachhakt, und die Bestaetigung
    fehlt am Ende in der Pruefung.

    Jetzt sagt die Antwort, dass der Versuch **festgehalten**, nicht versendet
    wurde: Der Nachweis, dass jemand erinnern wollte, ist etwas wert; die
    Behauptung, es sei versendet, ist es nicht.
    """

    erinnerung_vermerkt: bool
    #: ``NICHT_KONFIGURIERT``, solange kein Versandweg angebunden ist.
    versand: str
    versuche: int
    angefordert_am: Optional[str] = None
    hinweis: str
    token: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict:
    d = dict(row._mapping)
    # Normalise date fields to ISO strings
    for key in ("versanddatum", "erinnerung_am", "erhalten_am", "created_at"):
        if key in d and d[key] is not None:
            val = d[key]
            if hasattr(val, "isoformat"):
                d[key] = val.isoformat()
    return d


def _gen_token() -> str:
    return str(uuid4()).replace("-", "")[:8].upper()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", summary="Gelangensbestätigungen auflisten",
    response_model=list[GelangensbestaetigungOut]
)
def list_gelangensbestaetigung(
    status: Optional[str] = Query(None, description="AUSSTEHEND | ERHALTEN | ABGELAUFEN"),
    lieferschein_nr: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    # Der Mandant ist nicht optional: Eine Gelangensbestaetigung enthaelt
    # Kundennummer, Empfaengername und die USt-IdNr. eines Dritten.
    where_clauses = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if status:
        where_clauses.append("status = :status")
        params["status"] = status
    if lieferschein_nr:
        where_clauses.append("lieferschein_nr = :lieferschein_nr")
        params["lieferschein_nr"] = lieferschein_nr

    where_sql = "WHERE " + " AND ".join(where_clauses)

    try:
        rows = db.execute(
            text(
                f"SELECT id, lieferschein_nr, rechnung_nr, kunde_nr, bestimmungsland_code, "
                f"warenwert_eur, versanddatum, empfaenger_name, empfaenger_ust_id_nr, "
                f"status, token, erinnerung_am, erhalten_am "
                f"FROM domain_compliance.gelangensbestaetigung "
                f"{where_sql} "
                f"ORDER BY versanddatum DESC"  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
            ),
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        # Keine leere Liste: "kein Nachweis erfasst" und "die Tabelle ist nicht
        # lesbar" sahen gleich aus. Ohne Gelangensbestaetigung entfaellt die
        # Steuerfreiheit der innergemeinschaftlichen Lieferung (§ 6a UStG,
        # § 17a UStDV) — das darf kein stiller Leerstand sein.
        db.rollback()
        logger.exception("Gelangensbestaetigungen nicht lesbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        ) from exc


@router.post("", status_code=201, summary="Gelangensbestätigung erstellen",
    response_model=GelangensbestaetigungCreateOut
)
def create_gelangensbestaetigung(
    payload: GelangensbestaetigungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    entry_id = str(uuid4())
    token = _gen_token()
    erinnerung_am = payload.versanddatum + timedelta(days=ERINNERUNG_TAGE)

    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.gelangensbestaetigung "
                "(id, tenant_id, lieferschein_nr, rechnung_nr, kunde_nr, bestimmungsland_code, "
                "warenwert_eur, versanddatum, empfaenger_name, empfaenger_ust_id_nr, "
                "status, token, erinnerung_am, erhalten_am, created_at) "
                "VALUES (:id, :tenant_id, :lieferschein_nr, :rechnung_nr, :kunde_nr, :bestimmungsland_code, "
                ":warenwert_eur, :versanddatum, :empfaenger_name, :empfaenger_ust_id_nr, "
                "'AUSSTEHEND', :token, :erinnerung_am, NULL, NOW())"
            ),
            {
                "id": entry_id,
                "tenant_id": tenant_id,
                "lieferschein_nr": payload.lieferschein_nr,
                "rechnung_nr": payload.rechnung_nr,
                "kunde_nr": payload.kunde_nr,
                "bestimmungsland_code": payload.bestimmungsland_code,
                "warenwert_eur": payload.warenwert_eur,
                "versanddatum": payload.versanddatum,
                "empfaenger_name": payload.empfaenger_name,
                "empfaenger_ust_id_nr": payload.empfaenger_ust_id_nr,
                "token": token,
                "erinnerung_am": erinnerung_am,
            },
        )
        db.commit()
        return {
            "id": entry_id,
            "token": token,
            "erinnerung_am": erinnerung_am.isoformat(),
            "status": "AUSSTEHEND",
        }
    except Exception as exc:
        db.rollback()
        logger.error("Fehler beim Erstellen der Gelangensbestätigung: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.post("/{entry_id}/bestaetigen", summary="Gelangensbestätigung durch Empfänger bestätigen",
    response_model=IDResponse
)
def bestaetigen(
    entry_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    erhalten_am = datetime.now(timezone.utc).date()
    try:
        result = db.execute(
            text(
                "UPDATE domain_compliance.gelangensbestaetigung "
                "SET status = 'ERHALTEN', erhalten_am = :erhalten_am "
                "WHERE id = :id AND tenant_id = :tenant_id AND status = 'AUSSTEHEND'"
            ),
            {"id": entry_id, "tenant_id": tenant_id, "erhalten_am": erhalten_am},
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Gelangensbestätigung nicht gefunden oder bereits bearbeitet",
            )
        return {"id": entry_id, "status": "ERHALTEN", "erhalten_am": erhalten_am.isoformat()}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.get("/faellig", summary="Überfällige Gelangensbestätigungen",
    response_model=list[GelangensbestaetigungFaelligOut]
)
def list_faellig(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    today = date.today()
    try:
        rows = db.execute(
            text(
                "SELECT id, lieferschein_nr, rechnung_nr, kunde_nr, empfaenger_name, "
                "bestimmungsland_code, warenwert_eur, versanddatum, token, erinnerung_am "
                "FROM domain_compliance.gelangensbestaetigung "
                "WHERE tenant_id = :tenant_id AND status = 'AUSSTEHEND' "
                "  AND erinnerung_am <= :today "
                "ORDER BY erinnerung_am ASC"
            ),
            {"tenant_id": tenant_id, "today": today},
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        # Das ist die Liste, die sagt, was nachzufassen ist. Ein leeres Ergebnis
        # heisst "nichts nachzufassen" — mit Steuerwirkung, wenn es nicht stimmt.
        db.rollback()
        logger.exception("Faellige Gelangensbestaetigungen nicht lesbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        ) from exc


#: Solange kein Versandweg (E-Mail, Fax) angebunden ist, ist dies die Wahrheit
#: ueber die Erinnerung. Sie steht in der Antwort, damit niemand annimmt, der
#: Empfaenger sei angeschrieben worden.
VERSAND_UNKONFIGURIERT = "NICHT_KONFIGURIERT"


@router.post(
    "/{entry_id}/mahnung",
    response_model=MahnungOut,
    summary="Erinnerung vermerken",
)
def mahnung_senden(
    entry_id: str,
    angefordert_durch: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Haelt fest, dass an die Gelangensbestaetigung erinnert werden soll.

    Es wird **nichts versendet** — es ist kein Versandweg angebunden. Vorher
    antwortete dieser Weg ``erinnerung_gesendet: true`` und tat nichts; die
    Erinnerung ist Teil der Nachweiskette nach § 17a UStDV, und eine falsche
    Quittung heisst, dass niemand mehr nachhakt.

    Festgehalten werden Zeitpunkt, Anzahl der Versuche und wer sie angefordert
    hat. Das ist der Nachweis, dass erinnert werden sollte.
    """
    try:
        row = db.execute(
            text(
                "UPDATE domain_compliance.gelangensbestaetigung "
                "SET erinnerung_angefordert_am = NOW(), "
                "    erinnerung_versuche = COALESCE(erinnerung_versuche, 0) + 1, "
                "    erinnerung_angefordert_durch = :durch "
                "WHERE id = :id AND tenant_id = :tenant_id "
                "RETURNING token, erinnerung_versuche, erinnerung_angefordert_am"
            ),
            {"id": entry_id, "tenant_id": tenant_id, "durch": angefordert_durch},
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )
    if not row:
        raise HTTPException(status_code=404, detail="Gelangensbestätigung nicht gefunden")

    logger.info(
        "Erinnerung an Gelangensbestaetigung %s vermerkt (Versuch %s, kein Versandweg)",
        entry_id, row.erinnerung_versuche,
    )
    return {
        "erinnerung_vermerkt": True,
        "versand": VERSAND_UNKONFIGURIERT,
        "versuche": int(row.erinnerung_versuche or 0),
        "angefordert_am": (
            row.erinnerung_angefordert_am.isoformat()
            if row.erinnerung_angefordert_am else None
        ),
        "hinweis": (
            "Es ist kein Versandweg angebunden. Der Empfaenger ist zu unterrichten; "
            "dieser Vermerk haelt nur fest, dass erinnert werden soll."
        ),
        "token": row.token,
    }
