"""
Sanctions Compliance API — Verbotsliste / Sanktionsprüfung
Agrar-Spezialsoftware Feature: EU/UN/US/HM_TREASURY sanctions list management.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance/sanctions", tags=["Compliance", "Sanctions"])

MIGRATION_HINT = (
    "Tabelle domain_compliance.sanctions_list fehlt — "
    "bitte Alembic-Migration ausführen: alembic upgrade head"
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class SanktionsEintragCreate(BaseModel):
    name: str
    alias_namen: list[str] = Field(default_factory=list)
    land_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    liste: str = Field(..., description="EU | UN | OFAC | HM_TREASURY")
    eintragstyp: str = Field(
        ..., description="PERSON | ORGANISATION | SCHIFF | ANDERES"
    )
    eintrags_nr: str
    is_active: bool = True


class SanktionsPruefungInput(BaseModel):
    name: str
    land_code: Optional[str] = None
    adresse: Optional[str] = None


class SanktionsTreffer(BaseModel):
    name: str
    liste: str
    eintrags_nr: str
    aehnlichkeit: float


class SanktionsPruefungResult(BaseModel):
    geprueft_am: str
    treffer: list[SanktionsTreffer]
    status: str  # KEIN_TREFFER | VERDAECHTIG | TREFFER
    empfehlung: str


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict:
    return dict(row._mapping)


def _fuzzy_match(input_name: str, eintraege: list[dict]) -> list[SanktionsTreffer]:
    """Simple case-insensitive match + alias check + 5-char prefix partial match."""
    input_lower = input_name.lower().strip()
    input_prefix = input_lower[:5]
    treffer: list[SanktionsTreffer] = []

    for e in eintraege:
        candidate = e.get("name", "")
        aliases: list[str] = e.get("alias_namen") or []
        if isinstance(aliases, str):
            # stored as comma-separated string fallback
            aliases = [a.strip() for a in aliases.split(",") if a.strip()]

        all_names = [candidate] + aliases

        for n in all_names:
            n_lower = n.lower().strip()
            if input_lower == n_lower:
                aehnlichkeit = 1.0
            elif input_lower in n_lower or n_lower in input_lower:
                aehnlichkeit = 0.8
            elif input_prefix and n_lower[:5] == input_prefix:
                aehnlichkeit = 0.5
            else:
                continue

            treffer.append(
                SanktionsTreffer(
                    name=candidate,
                    liste=e.get("liste", ""),
                    eintrags_nr=e.get("eintrags_nr", ""),
                    aehnlichkeit=aehnlichkeit,
                )
            )
            break  # one hit per entry is enough

    return treffer


def _status_from_treffer(treffer: list[SanktionsTreffer]) -> str:
    if not treffer:
        return "KEIN_TREFFER"
    max_sim = max(t.aehnlichkeit for t in treffer)
    if max_sim >= 1.0:
        return "TREFFER"
    return "VERDAECHTIG"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/eintraege", summary="Sanktionsliste abfragen")
def list_eintraege(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id, name, alias_namen, land_code, liste, eintragstyp, "
                "eintrags_nr, is_active, created_at "
                "FROM domain_compliance.sanctions_list "
                "WHERE is_active = TRUE "
                "ORDER BY name"
            )
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("sanctions_list table not accessible: %s", exc)
        return []


@router.post("/eintraege", status_code=201, summary="Sanktionseintrag anlegen")
def create_eintrag(
    payload: SanktionsEintragCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    entry_id = str(uuid4())
    aliases_str = ",".join(payload.alias_namen)
    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.sanctions_list "
                "(id, name, alias_namen, land_code, liste, eintragstyp, eintrags_nr, is_active, created_at) "
                "VALUES (:id, :name, :alias_namen, :land_code, :liste, :eintragstyp, :eintrags_nr, :is_active, NOW())"
            ),
            {
                "id": entry_id,
                "name": payload.name,
                "alias_namen": aliases_str,
                "land_code": payload.land_code,
                "liste": payload.liste,
                "eintragstyp": payload.eintragstyp,
                "eintrags_nr": payload.eintrags_nr,
                "is_active": payload.is_active,
            },
        )
        db.commit()
        return {"id": entry_id, "eintrags_nr": payload.eintrags_nr, "status": "angelegt"}
    except Exception as exc:
        db.rollback()
        logger.error("Fehler beim Anlegen des Sanktionseintrags: %s", exc)
        raise HTTPException(status_code=503, detail={"error": str(exc), "migration_hint": MIGRATION_HINT})


@router.post("/pruefen", summary="Name gegen Sanktionsliste prüfen")
def pruefen(
    payload: SanktionsPruefungInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> SanktionsPruefungResult:
    geprueft_am = datetime.now(timezone.utc).isoformat()
    try:
        rows = db.execute(
            text(
                "SELECT name, alias_namen, liste, eintrags_nr "
                "FROM domain_compliance.sanctions_list "
                "WHERE is_active = TRUE"
            )
        ).fetchall()
        eintraege = [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("sanctions_list not accessible during pruefen: %s", exc)
        return SanktionsPruefungResult(
            geprueft_am=geprueft_am,
            treffer=[],
            status="KEIN_TREFFER",
            empfehlung=f"Prüfung nicht möglich — {MIGRATION_HINT}",
        )

    treffer = _fuzzy_match(payload.name, eintraege)
    status = _status_from_treffer(treffer)

    empfehlungen = {
        "TREFFER": "Geschäftsbeziehung NICHT eingehen — Sanktionstreffer vorhanden. Compliance-Beauftragten informieren.",
        "VERDAECHTIG": "Verdächtiger Treffer — manuelle Prüfung durch Compliance-Beauftragten erforderlich.",
        "KEIN_TREFFER": "Kein Sanktionstreffer — Freigabe unter Vorbehalt periodischer Neuprüfung.",
    }

    # Log check to protocol table (best-effort)
    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.sanctions_checks "
                "(id, geprueft_name, status, geprueft_am) "
                "VALUES (:id, :name, :status, NOW())"
            ),
            {"id": str(uuid4()), "name": payload.name, "status": status},
        )
        db.commit()
    except Exception:
        db.rollback()

    return SanktionsPruefungResult(
        geprueft_am=geprueft_am,
        treffer=treffer,
        status=status,
        empfehlung=empfehlungen[status],
    )


@router.get("/pruefprotokoll", summary="Sanktionsprüf-Protokoll abrufen")
def pruefprotokoll(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id, geprueft_name, status, geprueft_am "
                "FROM domain_compliance.sanctions_checks "
                "ORDER BY geprueft_am DESC "
                "LIMIT 500"
            )
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("sanctions_checks table not accessible: %s", exc)
        return []
