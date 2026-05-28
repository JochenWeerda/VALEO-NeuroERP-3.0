"""Service-Anfragen API — CRUD for service requests, feedback, and case closure."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/service", tags=["Service"])

# ── Schemas ─────────────────────────────────────────────────────────────

class ServiceAnfrageCreate(BaseModel):
    nummer: str | None = None
    kunde: str
    betreff: str
    beschreibung: str | None = None
    prioritaet: str = "normal"  # hoch | normal | niedrig
    kategorie: str | None = None


class ServiceAnfrageUpdate(BaseModel):
    kunde: str | None = None
    betreff: str | None = None
    beschreibung: str | None = None
    prioritaet: str | None = None
    kategorie: str | None = None
    status: str | None = None


class RueckmeldungCreate(BaseModel):
    anfrage_id: str
    text: str
    bewertet_von: str | None = None
    bewertung: int | None = None  # 1-5


class AbschlussCreate(BaseModel):
    anfrage_id: str
    abschluss_grund: str | None = None
    notiz: str | None = None


# ── In-memory store ─────────────────────────────────────────────────────

_store: dict[str, dict] = {}
_rueckmeldungen: list[dict] = []
_counter = 0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_if_empty() -> None:
    global _counter
    if _store:
        return
    for item in [
        {
            "id": str(uuid4()),
            "nummer": "SR-2026-001",
            "kunde": "Landhandel Nord",
            "betreff": "Lieferverzögerung",
            "beschreibung": "Lieferung 3 Tage überfällig",
            "prioritaet": "hoch",
            "kategorie": "Logistik",
            "status": "neu",
            "datum": "2026-02-10",
            "tenant_id": "default",
            "created_at": "2026-02-10T08:00:00+00:00",
        },
        {
            "id": str(uuid4()),
            "nummer": "SR-2026-002",
            "kunde": "Agrar Müller",
            "betreff": "Qualitätsreklamation",
            "beschreibung": "Feuchtigkeitswert über Toleranz",
            "prioritaet": "normal",
            "kategorie": "Qualität",
            "status": "in-bearbeitung",
            "datum": "2026-02-09",
            "tenant_id": "default",
            "created_at": "2026-02-09T10:30:00+00:00",
        },
    ]:
        _store[item["id"]] = item
    _counter = 2


# ── Endpoints ───────────────────────────────────────────────────────────


@router.get("/anfragen", response_model=CompatFlexOut, summary="Anfragen auflisten")
async def list_anfragen(
    status: Optional[str] = Query(None),
    prioritaet: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> dict:
    """Liste aller Service-Anfragen (tenant-isoliert, paginiert)."""
    _seed_if_empty()
    items = [v for v in _store.values() if v.get("tenant_id") == x_tenant_id]
    if status:
        items = [i for i in items if i.get("status") == status]
    if prioritaet:
        items = [i for i in items if i.get("prioritaet") == prioritaet]
    total = len(items)
    items = sorted(items, key=lambda i: i.get("created_at", ""), reverse=True)
    items = items[skip : skip + limit]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/anfragen/{anfrage_id}", response_model=CompatFlexOut, summary="Anfrage abrufen")
async def get_anfrage(
    anfrage_id: str,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> dict:
    """Detail einer Service-Anfrage."""
    _seed_if_empty()
    item = _store.get(anfrage_id)
    if not item or item.get("tenant_id") != x_tenant_id:
        raise HTTPException(status_code=404, detail="Service-Anfrage nicht gefunden")
    return item


@router.post("/anfragen", response_model=CompatFlexOut, status_code=201, summary="Anfrage anlegen")
async def create_anfrage(
    body: ServiceAnfrageCreate,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> dict:
    """Neue Service-Anfrage anlegen."""
    global _counter
    _seed_if_empty()
    _counter += 1
    now = _now_iso()
    item = {
        "id": str(uuid4()),
        "nummer": body.nummer or f"SR-2026-{_counter:03d}",
        "kunde": body.kunde,
        "betreff": body.betreff,
        "beschreibung": body.beschreibung or "",
        "prioritaet": body.prioritaet,
        "kategorie": body.kategorie or "",
        "status": "neu",
        "datum": now[:10],
        "tenant_id": x_tenant_id,
        "created_at": now,
    }
    _store[item["id"]] = item
    return item


@router.put("/anfragen/{anfrage_id}", response_model=CompatFlexOut, summary="Anfrage aktualisieren")
async def update_anfrage(
    anfrage_id: str,
    body: ServiceAnfrageUpdate,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> dict:
    """Service-Anfrage aktualisieren."""
    _seed_if_empty()
    item = _store.get(anfrage_id)
    if not item or item.get("tenant_id") != x_tenant_id:
        raise HTTPException(status_code=404, detail="Service-Anfrage nicht gefunden")
    updates = body.model_dump(exclude_unset=True)
    item.update(updates)
    item["updated_at"] = _now_iso()
    return item


@router.delete("/anfragen/{anfrage_id}", response_class=Response, status_code=204, response_model=None, summary="Anfrage löschen")
async def delete_anfrage(
    anfrage_id: str,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> Response:
    """Service-Anfrage löschen."""
    _seed_if_empty()
    item = _store.get(anfrage_id)
    if not item or item.get("tenant_id") != x_tenant_id:
        raise HTTPException(status_code=404, detail="Service-Anfrage nicht gefunden")
    del _store[anfrage_id]
    return Response(status_code=204)


@router.post("/rueckmeldungen", response_model=CompatFlexOut, status_code=201, summary="Rueckmeldung anlegen")
async def create_rueckmeldung(
    body: RueckmeldungCreate,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> dict:
    """Rückmeldung zu einer Service-Anfrage erfassen."""
    _seed_if_empty()
    item = _store.get(body.anfrage_id)
    if not item or item.get("tenant_id") != x_tenant_id:
        raise HTTPException(status_code=404, detail="Service-Anfrage nicht gefunden")
    rm = {
        "id": str(uuid4()),
        "anfrage_id": body.anfrage_id,
        "text": body.text,
        "bewertet_von": body.bewertet_von,
        "bewertung": body.bewertung,
        "created_at": _now_iso(),
    }
    _rueckmeldungen.append(rm)
    return rm


@router.post("/abschluss", response_model=CompatFlexOut, summary="Service case abschließen")
async def close_service_case(
    body: AbschlussCreate,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
) -> dict:
    """Service-Fall abschließen."""
    _seed_if_empty()
    item = _store.get(body.anfrage_id)
    if not item or item.get("tenant_id") != x_tenant_id:
        raise HTTPException(status_code=404, detail="Service-Anfrage nicht gefunden")
    item["status"] = "erledigt"
    item["abschluss_grund"] = body.abschluss_grund or ""
    item["abschluss_notiz"] = body.notiz or ""
    item["abgeschlossen_am"] = _now_iso()
    return item
