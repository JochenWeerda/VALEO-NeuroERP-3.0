"""TAPI/Telefonie — eingehende Anrufe + Kunden-Auflösung für Click-to-Customer.

Ein lokaler TAPI-Bridge-Dienst meldet eingehende Anrufe (POST /incoming). Die
Rufnummer wird normalisiert und gegen public.kunden.tel aufgelöst. Das Frontend
pollt /pending und zeigt ein Popup mit dem erkannten Kunden; /ack quittiert.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends
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


@router.post("/incoming", summary="Eingehenden Anruf melden (TAPI-Bridge)")
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
    r = db.execute(text(f"SELECT {_COLS} FROM public.tapi_calls WHERE id = :id"), {"id": new_id}).mappings().first()
    return _row(r)


@router.get("/pending", summary="Offene (nicht quittierte) Anrufe")
def pending(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, Any]]:
    rows = db.execute(
        text(f"SELECT {_COLS} FROM public.tapi_calls WHERE tenant_id = :t AND acked = FALSE ORDER BY created_at DESC LIMIT 20"),
        {"t": tenant_id},
    ).mappings().all()
    return [_row(r) for r in rows]


@router.post("/{call_id}/ack", summary="Anruf quittieren")
def ack(call_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    db.execute(
        text("UPDATE public.tapi_calls SET acked = TRUE, status = 'erledigt', updated_at = now() WHERE id = :id AND tenant_id = :t"),
        {"id": call_id, "t": tenant_id},
    )
    db.commit()
    return {"ok": True}
