"""Service-Anfragen API — CRUD for service requests, feedback, and case closure.

Gespeichert in ``domain_ops.service_anfragen`` und ``domain_ops.service_anfrage_rueckmeldungen``. Bis 27.10.2026 lag
alles in einem Woerterbuch des Prozesses, vorbelegt mit zwei erfundenen Anfragen des Mandanten ``default``; nach jedem
Neustart war jede angelegte Anfrage weg. Mandant und Bearbeiter kommen aus dem Token.
"""

from typing import Any, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.schemas.service_anfragen_schemas import ServiceAnfragenOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.akteur import gepruefter_akteur_aus_request
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/service", tags=["Service"])

Prioritaet = Literal["hoch", "normal", "niedrig"]
Status = Literal["neu", "in-bearbeitung", "erledigt"]

_SPALTEN = (
    "id, tenant_id, nummer, kunde, betreff, beschreibung, prioritaet, kategorie, status, datum, "
    "abschluss_grund, abschluss_notiz, abgeschlossen_am, erstellt_von, created_at, updated_at"
)

# ── Schemas ─────────────────────────────────────────────────────────────

class ServiceAnfrageCreate(BaseModel):
    nummer: str | None = Field(default=None, max_length=40)
    kunde: str = Field(min_length=1, max_length=255)
    betreff: str = Field(min_length=1, max_length=255)
    beschreibung: str | None = None
    prioritaet: Prioritaet = "normal"
    kategorie: str | None = Field(default=None, max_length=120)


class ServiceAnfrageUpdate(BaseModel):
    kunde: str | None = Field(default=None, min_length=1, max_length=255)
    betreff: str | None = Field(default=None, min_length=1, max_length=255)
    beschreibung: str | None = None
    prioritaet: Prioritaet | None = None
    kategorie: str | None = Field(default=None, max_length=120)
    #: "erledigt" nur ueber ``/abschluss`` — dort entstehen Grund und Zeitpunkt.
    status: Literal["neu", "in-bearbeitung"] | None = None


class RueckmeldungCreate(BaseModel):
    anfrage_id: str
    text: str = Field(min_length=1)
    bewertet_von: str | None = Field(default=None, max_length=255)
    bewertung: int | None = Field(default=None, ge=1, le=5)


class AbschlussCreate(BaseModel):
    anfrage_id: str
    abschluss_grund: str | None = None
    notiz: str | None = None


def _json(row: Any) -> dict:
    return {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(row).items()}


def _lies(db: Session, anfrage_id: str, tenant_id: str, *, sperren: bool = False) -> dict:
    sql = f"SELECT {_SPALTEN} FROM domain_ops.service_anfragen WHERE id = :id AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal, Werte sind gebunden
    row = db.execute(text(sql + (" FOR UPDATE" if sperren else "")), {"id": anfrage_id, "tid": tenant_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Service-Anfrage nicht gefunden")
    return dict(row)


def _naechste_nummer(db: Session, tenant_id: str) -> str:
    """SR-<Jahr>-<laufend> je Mandant; die Sperre haelt zwei gleichzeitige Anlagen auseinander."""
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:k))"), {"k": f"service_anfragen:{tenant_id}"})
    jahr = db.execute(text("SELECT EXTRACT(YEAR FROM CURRENT_DATE)::int")).scalar()
    zuletzt = db.execute(
        text(
            "SELECT COALESCE(MAX(CAST(SUBSTRING(nummer FROM '^SR-[0-9]{4}-([0-9]+)$') AS integer)), 0) "
            "FROM domain_ops.service_anfragen WHERE tenant_id = :tid AND nummer LIKE :muster"
        ),
        {"tid": tenant_id, "muster": f"SR-{jahr}-%"},
    ).scalar()
    return f"SR-{jahr}-{int(zuletzt) + 1:03d}"


# ── Endpoints ───────────────────────────────────────────────────────────


@router.get("/anfragen", response_model=ServiceAnfragenOut, summary="Anfragen auflisten")
async def list_anfragen(
    status: Optional[str] = Query(None),
    prioritaet: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Liste aller Service-Anfragen (tenant-isoliert, paginiert)."""
    bedingung = "tenant_id = :tid"
    params: dict[str, Any] = {"tid": tenant_id, "skip": skip, "limit": limit}
    if status:
        bedingung += " AND status = :status"
        params["status"] = status
    if prioritaet:
        bedingung += " AND prioritaet = :prioritaet"
        params["prioritaet"] = prioritaet
    total = db.execute(text(f"SELECT COUNT(*) FROM domain_ops.service_anfragen WHERE {bedingung}"), params).scalar()  # nosec B608  # reviewed-safe: Bedingung aus Code-Literalen, Werte gebunden
    rows = db.execute(
        text(f"SELECT {_SPALTEN} FROM domain_ops.service_anfragen WHERE {bedingung} "  # nosec B608  # reviewed-safe: wie oben
             "ORDER BY created_at DESC, nummer DESC OFFSET :skip LIMIT :limit"),
        params,
    ).mappings().all()
    return {"items": [_json(r) for r in rows], "total": int(total or 0), "skip": skip, "limit": limit}


@router.get("/anfragen/{anfrage_id}", response_model=ServiceAnfragenOut, summary="Anfrage abrufen")
async def get_anfrage(
    anfrage_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Detail einer Service-Anfrage mit ihren Rueckmeldungen."""
    item = _json(_lies(db, anfrage_id, tenant_id))
    item["rueckmeldungen"] = [
        _json(r) for r in db.execute(
            text("SELECT id, anfrage_id, text, bewertet_von, bewertung, erstellt_von, created_at "
                 "FROM domain_ops.service_anfrage_rueckmeldungen WHERE anfrage_id = :id AND tenant_id = :tid "
                 "ORDER BY created_at"),
            {"id": anfrage_id, "tid": tenant_id},
        ).mappings()
    ]
    return item


@router.post("/anfragen", response_model=ServiceAnfragenOut, status_code=201, summary="Anfrage anlegen", dependencies=SCHREIBEN["FACHLICH"])
async def create_anfrage(
    body: ServiceAnfrageCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Neue Service-Anfrage anlegen."""
    akteur = gepruefter_akteur_aus_request(request)
    nummer = (body.nummer or "").strip() or _naechste_nummer(db, tenant_id)
    try:
        row = db.execute(
            text(f"""
                INSERT INTO domain_ops.service_anfragen
                    (id, tenant_id, nummer, kunde, betreff, beschreibung, prioritaet, kategorie, erstellt_von)
                VALUES (:id, :tid, :nummer, :kunde, :betreff, :beschreibung, :prioritaet, :kategorie, :akteur)
                RETURNING {_SPALTEN}
            """),  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal, Werte sind gebunden
            {"id": str(uuid4()), "tid": tenant_id, "nummer": nummer, "kunde": body.kunde, "betreff": body.betreff,
             "beschreibung": body.beschreibung, "prioritaet": body.prioritaet, "kategorie": body.kategorie,
             "akteur": akteur},
        ).mappings().one()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Service-Anfrage {nummer} gibt es bereits.") from exc
    return _json(row)


@router.put("/anfragen/{anfrage_id}", response_model=ServiceAnfragenOut, summary="Anfrage aktualisieren", dependencies=SCHREIBEN["FACHLICH"])
async def update_anfrage(
    anfrage_id: str,
    body: ServiceAnfrageUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Service-Anfrage aktualisieren. Eine erledigte Anfrage bleibt, wie sie abgeschlossen wurde."""
    alt = _lies(db, anfrage_id, tenant_id, sperren=True)
    if alt["status"] == "erledigt":
        raise HTTPException(status_code=409, detail="Die Service-Anfrage ist abgeschlossen.")
    aenderung = body.model_dump(exclude_unset=True)
    if aenderung:
        zuweisung = ", ".join(f"{feld} = :{feld}" for feld in aenderung)  # Felder aus dem Modell, nie vom Client benannt
        row = db.execute(
            text(f"UPDATE domain_ops.service_anfragen SET {zuweisung}, updated_at = NOW() "  # nosec B608  # reviewed-safe: Feldnamen aus dem Pydantic-Modell
                 f"WHERE id = :id AND tenant_id = :tid RETURNING {_SPALTEN}"),
            {**aenderung, "id": anfrage_id, "tid": tenant_id},
        ).mappings().one()
        db.commit()
        return _json(row)
    return _json(alt)


@router.delete("/anfragen/{anfrage_id}", response_class=Response, status_code=204, response_model=None, summary="Anfrage löschen", dependencies=SCHREIBEN["FACHLICH"])
async def delete_anfrage(
    anfrage_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    """Service-Anfrage loeschen (mit ihren Rueckmeldungen)."""
    _lies(db, anfrage_id, tenant_id, sperren=True)
    db.execute(text("DELETE FROM domain_ops.service_anfragen WHERE id = :id AND tenant_id = :tid"),
               {"id": anfrage_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


@router.post("/rueckmeldungen", response_model=ServiceAnfragenOut, status_code=201, summary="Rueckmeldung anlegen", dependencies=SCHREIBEN["FACHLICH"])
async def create_rueckmeldung(
    body: RueckmeldungCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Rückmeldung zu einer Service-Anfrage erfassen."""
    akteur = gepruefter_akteur_aus_request(request)
    _lies(db, body.anfrage_id, tenant_id)
    row = db.execute(
        text("""
            INSERT INTO domain_ops.service_anfrage_rueckmeldungen
                (id, tenant_id, anfrage_id, text, bewertet_von, bewertung, erstellt_von)
            VALUES (:id, :tid, :anfrage, :text, :von, :bewertung, :akteur)
            RETURNING id, anfrage_id, text, bewertet_von, bewertung, erstellt_von, created_at
        """),
        {"id": str(uuid4()), "tid": tenant_id, "anfrage": body.anfrage_id, "text": body.text,
         "von": body.bewertet_von, "bewertung": body.bewertung, "akteur": akteur},
    ).mappings().one()
    db.commit()
    return _json(row)


@router.post("/abschluss", response_model=ServiceAnfragenOut, summary="Service case abschließen", dependencies=SCHREIBEN["FACHLICH"])
async def close_service_case(
    body: AbschlussCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Service-Fall abschließen."""
    alt = _lies(db, body.anfrage_id, tenant_id, sperren=True)
    if alt["status"] == "erledigt":
        raise HTTPException(status_code=409, detail="Die Service-Anfrage ist bereits abgeschlossen.")
    row = db.execute(
        text(f"""
            UPDATE domain_ops.service_anfragen
            SET status = 'erledigt', abschluss_grund = :grund, abschluss_notiz = :notiz,
                abgeschlossen_am = NOW(), updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
            RETURNING {_SPALTEN}
        """),  # nosec B608  # reviewed-safe: Spaltenliste ist ein Code-Literal, Werte sind gebunden
        {"grund": body.abschluss_grund or "", "notiz": body.notiz or "", "id": body.anfrage_id, "tid": tenant_id},
    ).mappings().one()
    db.commit()
    return _json(row)
