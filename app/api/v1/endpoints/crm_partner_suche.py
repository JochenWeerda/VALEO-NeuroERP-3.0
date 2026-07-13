"""Einheitliche Partner-Suche über Kunden, Lieferanten und Leads (Multi-Rolle).

Ein Geschäftspartner kann gleichzeitig Kunde (z. B. Dünger) UND Lieferant (z. B.
Weizen) sein. Diese Suche unioniert die operativen Quellen und gruppiert über den
normalisierten Namen, sodass ein Treffer mehrere Rollen-Chips tragen kann
(kunde/lieferant/lead). Dünne Router-Schicht mit sqlalchemy.text().
"""

from __future__ import annotations

import re
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/crm/partner-suche", tags=["crm", "partner"])


def _norm(name: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _safe(db: Session, sql: str, params: dict) -> list[dict]:
    try:
        return [dict(r) for r in db.execute(text(sql), params).mappings().all()]
    except Exception:
        db.rollback()
        return []


@router.get("", response_model=list[dict[str, Any]], summary="Partner suchen (Kunde/Lieferant/Lead, Multi-Rolle)")
def partner_suche(
    q: str = Query("", description="Such-Token (Name/Nr.)"),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    like = f"%{q.strip()}%"
    has_q = bool(q.strip())

    # ── Kunden (kunden_lookup) ────────────────────────────────────────────
    kunden = _safe(
        db,
        "SELECT kunden_nr, name, plz, ort, business_partner_id FROM kunden_lookup "
        + ("WHERE name ILIKE :like OR matchcode ILIKE :like OR kunden_nr ILIKE :like " if has_q else "")
        + "ORDER BY name LIMIT :lim",
        {"like": like, "lim": limit * 2},
    )
    # ── Lieferanten (domain_einkauf.lieferanten) ──────────────────────────
    lieferanten = _safe(
        db,
        "SELECT partner_id, firmenname AS name, plz, ort FROM domain_einkauf.lieferanten "
        "WHERE aktiv IS NOT FALSE "
        + ("AND (firmenname ILIKE :like) " if has_q else "")
        + "ORDER BY firmenname LIMIT :lim",
        {"like": like, "lim": limit * 2},
    )
    # ── Leads (public.crm_leads) ──────────────────────────────────────────
    leads = _safe(
        db,
        "SELECT id, company AS name, NULL AS plz, NULL AS ort, status FROM public.crm_leads "
        + ("WHERE company ILIKE :like OR contact_person ILIKE :like " if has_q else "")
        + "ORDER BY company LIMIT :lim",
        {"like": like, "lim": limit * 2},
    )

    # ── Merge über normalisierten Namen (Multi-Rolle) ─────────────────────
    merged: dict[str, dict] = {}

    def slot(name: Optional[str]) -> dict:
        key = _norm(name)
        if key not in merged:
            merged[key] = {
                "name": name, "kunden_nr": None, "lieferanten_id": None, "lead_id": None,
                "business_partner_id": None, "plz": None, "ort": None, "rollen": [],
            }
        return merged[key]

    for k in kunden:
        s = slot(k["name"])
        s["kunden_nr"] = k["kunden_nr"]
        s["business_partner_id"] = s["business_partner_id"] or k.get("business_partner_id")
        s["plz"] = s["plz"] or k.get("plz")
        s["ort"] = s["ort"] or k.get("ort")
        if "kunde" not in s["rollen"]:
            s["rollen"].append("kunde")
    for l in lieferanten:
        s = slot(l["name"])
        s["lieferanten_id"] = str(l["partner_id"]) if l.get("partner_id") is not None else None
        s["plz"] = s["plz"] or l.get("plz")
        s["ort"] = s["ort"] or l.get("ort")
        if "lieferant" not in s["rollen"]:
            s["rollen"].append("lieferant")
    for ld in leads:
        s = slot(ld["name"])
        s["lead_id"] = str(ld["id"])
        if "lead" not in s["rollen"]:
            s["rollen"].append("lead")

    out = [v for v in merged.values() if v["name"]]
    # Mehrfachrollen zuerst, dann alphabetisch
    out.sort(key=lambda v: (-len(v["rollen"]), (v["name"] or "").lower()))
    return out[:limit]
