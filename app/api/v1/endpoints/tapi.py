"""TAPI/Telefonie — eingehende Anrufe + Kunden-Auflösung für Click-to-Customer.

Ein lokaler TAPI-Bridge-Dienst meldet eingehende Anrufe (POST /incoming). Die
Rufnummer wird normalisiert und gegen public.kunden.tel aufgelöst. Das Frontend
pollt /pending und zeigt ein Popup mit dem erkannten Kunden; /ack quittiert.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/crm/tapi", tags=["crm", "tapi"])

_COLS = "id, caller, called, richtung, kunden_nr, kunde_name, status, acked, created_at"


def _norm_phone(raw: str) -> str:
    """Auf Ziffern reduzieren; DE-Landesvorwahl/0 vereinheitlichen für den Vergleich."""
    d = re.sub(r"[^\d]", "", raw or "")
    if d.startswith("0049"):
        d = d[4:]
    elif d.startswith("49") and len(d) > 9:
        d = d[2:]
    elif d.startswith("0"):
        d = d[1:]
    return d


class IncomingIn(BaseModel):
    caller: str
    called: Optional[str] = None


def _resolve_kunde(db: Session, caller: str) -> Optional[dict]:
    norm = _norm_phone(caller)
    if len(norm) < 4:
        return None
    # letzte 7+ Ziffern matchen (robust gegen Vorwahl-Schreibweisen)
    tail = norm[-7:]
    try:
        r = db.execute(
            text(
                "SELECT kunden_nr, name1 AS name FROM public.kunden "
                "WHERE tel IS NOT NULL AND regexp_replace(tel, '[^0-9]', '', 'g') LIKE :tail "
                "ORDER BY length(tel) LIMIT 1"
            ),
            {"tail": f"%{tail}"},
        ).mappings().first()
    except Exception:
        db.rollback()
        return None
    return {"kunden_nr": r["kunden_nr"], "name": r["name"]} if r else None


def _row(r) -> dict:
    d = dict(r)
    d["id"] = str(d["id"])
    if d.get("created_at") is not None:
        d["created_at"] = d["created_at"].isoformat()
    return d


@router.post("/incoming", response_model=dict[str, Any], summary="Eingehenden Anruf melden (TAPI-Bridge)")
def incoming(body: IncomingIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    kunde = _resolve_kunde(db, body.caller)
    new_id = str(uuid.uuid4())
    db.execute(
        text(
            "INSERT INTO public.tapi_calls (id, caller, called, kunden_nr, kunde_name, tenant_id) "
            "VALUES (:id, :caller, :called, :knr, :kname, :tid)"
        ),
        {
            "id": new_id, "caller": body.caller, "called": body.called,
            "knr": (kunde or {}).get("kunden_nr"), "kname": (kunde or {}).get("name"), "tid": tenant_id,
        },
    )
    db.commit()
    # reviewed-safe: _COLS is a module-owned constant; all values remain bound parameters.
    r = db.execute(text(f"SELECT {_COLS} FROM public.tapi_calls WHERE id = :id"), {"id": new_id}).mappings().first()
    return _row(r)


@router.get("/pending", response_model=list[dict[str, Any]], summary="Offene (nicht quittierte) Anrufe")
def pending(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, Any]]:
    # reviewed-safe: _COLS is a module-owned constant; tenant data is bound.
    rows = db.execute(
        text(f"SELECT {_COLS} FROM public.tapi_calls WHERE tenant_id = :t AND acked = FALSE ORDER BY created_at DESC LIMIT 20"),
        {"t": tenant_id},
    ).mappings().all()
    return [_row(r) for r in rows]


@router.post("/{call_id}/ack", response_model=dict[str, Any], summary="Anruf quittieren")
def ack(call_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    db.execute(
        text("UPDATE public.tapi_calls SET acked = TRUE, status = 'erledigt', updated_at = now() WHERE id = :id AND tenant_id = :t"),
        {"id": call_id, "t": tenant_id},
    )
    db.commit()
    return {"ok": True}


# ── Ausgehende Wahl (Click-to-Dial) ───────────────────────────────────────────
# Das Cockpit fordert eine Wahl an; die lokale TAPI-Bridge pollt /dial/pending und
# loest den realen Call aus. Ohne Bridge bleibt die Anforderung eine protokollierte
# Absicht (graceful) — keine harte Hardware-Abhaengigkeit.
class DialIn(BaseModel):
    called: str
    kunden_nr: Optional[str] = None
    caller: Optional[str] = None


@router.post("/dial", response_model=dict[str, Any], summary="Ausgehende Wahl anfordern (Click-to-Dial)")
def dial(body: DialIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    if len(_norm_phone(body.called)) < 3:
        raise HTTPException(status_code=422, detail="Ungueltige Zielrufnummer")
    kunde_name: Optional[str] = None
    if body.kunden_nr:
        r = db.execute(
            text("SELECT name1 FROM public.kunden WHERE kunden_nr = :k"), {"k": body.kunden_nr}
        ).mappings().first()
        kunde_name = r["name1"] if r else None
    new_id = str(uuid.uuid4())
    # acked=TRUE -> erscheint NICHT im Eingangs-Popup (/pending); richtung='aus'.
    db.execute(
        text(
            "INSERT INTO public.tapi_calls (id, caller, called, richtung, kunden_nr, kunde_name, status, acked, tenant_id) "
            "VALUES (:id, :caller, :called, 'aus', :knr, :kname, 'dial_req', TRUE, :tid)"
        ),
        {
            # caller ist NOT NULL; bei ausgehender Wahl ist die eigene Nebenstelle
            # optional -> Sentinel 'KIM', bis die Bridge die reale Quelle setzt.
            "id": new_id, "caller": body.caller or "KIM", "called": body.called,
            "knr": body.kunden_nr, "kname": kunde_name, "tid": tenant_id,
        },
    )
    db.commit()
    # reviewed-safe: _COLS is a module-owned constant; all values remain bound parameters.
    r = db.execute(text(f"SELECT {_COLS} FROM public.tapi_calls WHERE id = :id"), {"id": new_id}).mappings().first()
    return _row(r)


@router.get("/dial/pending", response_model=list[dict[str, Any]], summary="Offene Wahl-Anforderungen (lokale Bridge)")
def dial_pending(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            f"SELECT {_COLS} FROM public.tapi_calls "
            "WHERE tenant_id = :t AND richtung = 'aus' AND status = 'dial_req' "
            "ORDER BY created_at LIMIT 20"
        ),
        {"t": tenant_id},
    ).mappings().all()
    return [_row(r) for r in rows]


@router.post("/dial/{call_id}/done", response_model=dict[str, Any], summary="Wahl ausgefuehrt quittieren")
def dial_done(call_id: str, status: str = "dialed", db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    db.execute(
        text("UPDATE public.tapi_calls SET status = :s, acked = TRUE, updated_at = now() WHERE id = :id AND tenant_id = :t"),
        {"s": status if status in {"dialed", "failed", "cancelled"} else "dialed", "id": call_id, "t": tenant_id},
    )
    db.commit()
    return {"ok": True}
