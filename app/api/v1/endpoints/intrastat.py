"""
Intrastat API — EU-Handelsstatistik
Meldepflicht für grenzüberschreitenden EU-Warenverkehr gemäß EU-Verordnung 638/2004.
INTRASTAT-DE Format für die Deutsche Bundesbank / Statistisches Bundesamt.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any, Optional
from uuid import uuid4

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema, IDResponse
from app.api.v1.schemas.intrastat_schemas import IntrastatOut


router = APIRouter(prefix="/intrastat", tags=["Intrastat", "Außenhandel"])

MIGRATION_HINT = (
    "Tabelle domain_compliance.intrastat_meldungen fehlt — "
    "bitte Alembic-Migration ausführen: alembic upgrade head"
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class IntrastatMeldungCreate(BaseModel):
    meldezeitraum: str = Field(..., description="YYYY-MM, z. B. 2026-04")
    meldungsart: str = Field(..., description="EINGANG | VERSENDUNG")
    cn8_warennummer: str = Field(..., min_length=8, max_length=8, description="8-stellige Kombinierte Nomenklatur")
    ursprungsland: str = Field(..., min_length=2, max_length=2)
    bestimmungsland: str = Field(..., min_length=2, max_length=2)
    statistischer_wert_eur: float = Field(..., gt=0)
    nettomasse_kg: float = Field(..., ge=0)
    menge: float = Field(..., gt=0)
    mengeneinheit: str = Field(..., max_length=10)
    geschaeftsvorgang_code: int = Field(
        ..., description="11=Kauf/Verkauf, 12=Lohnarbeit, 21=Rückware, …"
    )


class IntrastatMeldungOut(BaseModel):
    id: str
    meldenummer: str
    meldezeitraum: str
    meldungsart: str
    cn8_warennummer: str
    ursprungsland: str
    bestimmungsland: str
    statistischer_wert_eur: float
    nettomasse_kg: float
    menge: float
    mengeneinheit: str
    geschaeftsvorgang_code: int
    status: str  # ENTWURF | GEMELDET | KORRIGIERT


class IntrastatMeldungCreateOut(BaseModel):
    """Was das Anlegen zurueckgibt.

    Vorher stand hier ``IDResponse`` (``id`` und ``message``) — die
    **Meldenummer** fiel aus der Antwort heraus, also genau die Kennung, unter
    der die Meldung abgegeben wird. Sichtbar wurde das nicht, weil die fehlende
    Tabelle vorher 503 ergab.
    """

    id: str
    meldenummer: str
    status: str


class IntrastatMeldungUpdate(BaseModel):
    cn8_warennummer: Optional[str] = Field(None, min_length=8, max_length=8)
    ursprungsland: Optional[str] = Field(None, min_length=2, max_length=2)
    bestimmungsland: Optional[str] = Field(None, min_length=2, max_length=2)
    statistischer_wert_eur: Optional[float] = None
    nettomasse_kg: Optional[float] = None
    menge: Optional[float] = None
    mengeneinheit: Optional[str] = None
    geschaeftsvorgang_code: Optional[int] = None
    status: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict:
    return dict(row._mapping)


def _gen_meldenummer(db: Session, tenant_id: str, meldezeitraum: str, meldungsart: str) -> str:
    """Generate INTRASTAT-DE meldenummer: INT-{YYYYMM}-{E|V}-{seq:05d}"""
    ym = meldezeitraum.replace("-", "")
    art_code = "E" if meldungsart == "EINGANG" else "V"
    # Der Nummernkreis laeuft je Haus. Vorher zaehlte er ueber alle Haeuser:
    # Das zweite Haus begann dort, wo das erste stand, und die Nummern eines
    # Hauses hatten Luecken, die kein Pruefer erklaeren kann.
    #
    # Und kein "except: seq = 1": Eine Meldenummer zu raten, die es schon gibt,
    # ist schlechter als keine Meldung anzulegen. Die Eindeutigkeit je Haus und
    # Zeitraum haelt die Datenbank.
    row = db.execute(
        text(
            "SELECT COUNT(*) AS cnt FROM domain_compliance.intrastat_meldungen "
            "WHERE tenant_id = :tenant_id AND meldezeitraum = :meldezeitraum "
            "  AND meldungsart = :meldungsart"
        ),
        {"tenant_id": tenant_id, "meldezeitraum": meldezeitraum, "meldungsart": meldungsart},
    ).fetchone()
    seq = (row.cnt if row else 0) + 1
    return f"INT-{ym}-{art_code}-{seq:05d}"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/meldungen", summary="Intrastat-Meldungen auflisten",
    response_model=list[IntrastatOut]
)
def list_meldungen(
    meldezeitraum: Optional[str] = Query(None, description="YYYY-MM"),
    meldungsart: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    where_clauses = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if meldezeitraum:
        where_clauses.append("meldezeitraum = :meldezeitraum")
        params["meldezeitraum"] = meldezeitraum
    if meldungsart:
        where_clauses.append("meldungsart = :meldungsart")
        params["meldungsart"] = meldungsart

    where_sql = "WHERE " + " AND ".join(where_clauses)

    try:
        rows = db.execute(
            text(
                f"SELECT id, meldenummer, meldezeitraum, meldungsart, cn8_warennummer, "
                f"ursprungsland, bestimmungsland, statistischer_wert_eur, nettomasse_kg, "
                f"menge, mengeneinheit, geschaeftsvorgang_code, status "
                f"FROM domain_compliance.intrastat_meldungen "
                f"{where_sql} "
                f"ORDER BY meldezeitraum DESC, meldenummer"  # nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden
            ),
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        # Keine leere Liste: Eine Meldung, die im System steht und nicht
        # angezeigt wird, wird nicht abgegeben.
        db.rollback()
        logger.exception("Intrastat-Meldungen nicht lesbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        ) from exc


@router.post("/meldungen", status_code=201, summary="Intrastat-Meldung erstellen",
    response_model=IntrastatMeldungCreateOut
)
def create_meldung(
    payload: IntrastatMeldungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    entry_id = str(uuid4())
    meldenummer = _gen_meldenummer(db, tenant_id, payload.meldezeitraum, payload.meldungsart)

    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.intrastat_meldungen "
                "(id, tenant_id, meldenummer, meldezeitraum, meldungsart, cn8_warennummer, "
                "ursprungsland, bestimmungsland, statistischer_wert_eur, nettomasse_kg, "
                "menge, mengeneinheit, geschaeftsvorgang_code, status, created_at) "
                "VALUES (:id, :tenant_id, :meldenummer, :meldezeitraum, :meldungsart, :cn8, "
                ":ursprungsland, :bestimmungsland, :wert, :masse, "
                ":menge, :einheit, :gv_code, 'ENTWURF', NOW())"
            ),
            {
                "id": entry_id,
                "tenant_id": tenant_id,
                "meldenummer": meldenummer,
                "meldezeitraum": payload.meldezeitraum,
                "meldungsart": payload.meldungsart,
                "cn8": payload.cn8_warennummer,
                "ursprungsland": payload.ursprungsland,
                "bestimmungsland": payload.bestimmungsland,
                "wert": payload.statistischer_wert_eur,
                "masse": payload.nettomasse_kg,
                "menge": payload.menge,
                "einheit": payload.mengeneinheit,
                "gv_code": payload.geschaeftsvorgang_code,
            },
        )
        db.commit()
        return {"id": entry_id, "meldenummer": meldenummer, "status": "ENTWURF"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.put("/meldungen/{meldung_id}", summary="Intrastat-Meldung aktualisieren",
    response_model=IDResponse
)
def update_meldung(
    meldung_id: str,
    payload: IntrastatMeldungUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übergeben")

    db_col_map = {
        "cn8_warennummer": "cn8_warennummer",
        "ursprungsland": "ursprungsland",
        "bestimmungsland": "bestimmungsland",
        "statistischer_wert_eur": "statistischer_wert_eur",
        "nettomasse_kg": "nettomasse_kg",
        "menge": "menge",
        "mengeneinheit": "mengeneinheit",
        "geschaeftsvorgang_code": "geschaeftsvorgang_code",
        "status": "status",
    }
    set_clauses = ", ".join(f"{db_col_map[k]} = :{k}" for k in updates)
    params = {**updates, "id": meldung_id, "tenant_id": tenant_id}

    try:
        db.execute(
            text(
                f"UPDATE domain_compliance.intrastat_meldungen "
                f"SET {set_clauses} WHERE id = :id AND tenant_id = :tenant_id"  # nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden
            ),
            params,
        )
        db.commit()
        return {"id": meldung_id, "status": "aktualisiert"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.delete("/meldungen/{meldung_id}", status_code=204, summary="Intrastat-Entwurf löschen", response_class=Response, response_model=None)
def delete_meldung(
    meldung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> None:
    try:
        # Only ENTWURF may be deleted
        row = db.execute(
            text(
                "SELECT status FROM domain_compliance.intrastat_meldungen "
                "WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": meldung_id, "tenant_id": tenant_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Meldung nicht gefunden")
        if row.status != "ENTWURF":
            raise HTTPException(
                status_code=409,
                detail=f"Nur Entwürfe können gelöscht werden. Aktueller Status: {row.status}",
            )
        db.execute(
            text(
                "DELETE FROM domain_compliance.intrastat_meldungen "
                "WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": meldung_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.get("/meldungen/{meldezeitraum}/zusammenfassung", summary="Zusammenfassung nach Meldezeitraum",
    response_model=IntrastatOut
)
def zusammenfassung(
    meldezeitraum: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    try:
        rows = db.execute(
            text(
                "SELECT cn8_warennummer, meldungsart, "
                "COUNT(*) AS anzahl_positionen, "
                "SUM(statistischer_wert_eur) AS gesamtwert_eur, "
                "SUM(nettomasse_kg) AS gesamtmasse_kg, "
                "SUM(menge) AS gesamtmenge "
                "FROM domain_compliance.intrastat_meldungen "
                "WHERE tenant_id = :tenant_id AND meldezeitraum = :meldezeitraum "
                "GROUP BY cn8_warennummer, meldungsart "
                "ORDER BY cn8_warennummer"
            ),
            {"tenant_id": tenant_id, "meldezeitraum": meldezeitraum},
        ).fetchall()

        total_wert = sum(float(r.gesamtwert_eur or 0) for r in rows)
        return {
            "meldezeitraum": meldezeitraum,
            "positionen": [_row_to_dict(r) for r in rows],
            "total_wert_eur": total_wert,
        }
    except Exception as exc:
        # Keine Nullzusammenfassung: Sie ist die Grundlage der Meldung.
        db.rollback()
        logger.exception("Intrastat-Zusammenfassung nicht lesbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        ) from exc


@router.post(
    "/meldungen/{meldezeitraum}/export-csv",
    response_model=IntrastatOut,
    summary="Intrastat-Meldung als CSV exportieren (INTRASTAT-DE)",
)
def export_csv(
    meldezeitraum: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StreamingResponse:
    try:
        rows = db.execute(
            text(
                "SELECT meldenummer, cn8_warennummer, ursprungsland, bestimmungsland, "
                "statistischer_wert_eur, nettomasse_kg, menge, mengeneinheit, "
                "meldungsart, geschaeftsvorgang_code "
                "FROM domain_compliance.intrastat_meldungen "
                "WHERE tenant_id = :tenant_id AND meldezeitraum = :meldezeitraum "
                "ORDER BY meldenummer"
            ),
            # Ohne diesen Filter enthielt der Export eines Hauses die Zeilen
            # aller Haeuser — eine falsche Meldung an das Statistische
            # Bundesamt.
            {"tenant_id": tenant_id, "meldezeitraum": meldezeitraum},
        ).fetchall()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    # INTRASTAT-DE header
    writer.writerow([
        "meldenummer", "warennummer", "ursprungsland", "bestimmungsland",
        "statistischer_wert_eur", "nettomasse_kg", "menge", "mengeneinheit",
        "meldungsart", "geschaeftsvorgang_code",
    ])
    for r in rows:
        writer.writerow([
            r.meldenummer,
            r.cn8_warennummer,
            r.ursprungsland,
            r.bestimmungsland,
            f"{float(r.statistischer_wert_eur):.2f}",
            f"{float(r.nettomasse_kg):.3f}",
            f"{float(r.menge):.3f}",
            r.mengeneinheit,
            r.meldungsart,
            r.geschaeftsvorgang_code,
        ])

    output.seek(0)
    filename = f"intrastat_{meldezeitraum}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
