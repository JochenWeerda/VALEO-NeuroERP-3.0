"""FEED-QS-001 — Futtermittel QS: HACCP-Plaene, VLOG-Meldungen, QS-Leitfaden."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/futtermittel/qs", tags=["futtermittel", "qs"])


def _tenant(x_tenant_id: str | None = Header(None)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


# ── HACCP-Plaene ──────────────────────────────────────────────────────────────

@router.get("/haccp-plaene", response_model=list[dict[str, Any]], summary="HACCP-Plaene auflisten")
def list_haccp_plaene(
    aktiv: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM domain_shared.futtermittel_haccp_plaene WHERE tenant_id = :tid"
    params: dict[str, Any] = {"tid": tenant_id}
    if aktiv is not None:
        sql += " AND aktiv = :aktiv"
        params["aktiv"] = aktiv
    sql += " ORDER BY erstellt_am DESC LIMIT :limit"
    params["limit"] = limit
    try:
        rows = db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.get("/haccp-plaene/{plan_id}", response_model=dict[str, Any], summary="HACCP-Plan Detail")
def get_haccp_plan(
    plan_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    row = db.execute(
        text("SELECT * FROM domain_shared.futtermittel_haccp_plaene WHERE id = :id AND tenant_id = :tid"),
        {"id": plan_id, "tid": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="HACCP-Plan nicht gefunden")
    return dict(row)


@router.post("/haccp-plaene", response_model=dict[str, Any], status_code=201, summary="HACCP-Plan anlegen")
def create_haccp_plan(
    body: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    import uuid, json
    from datetime import date
    plan_id = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO domain_shared.futtermittel_haccp_plaene
            (id, tenant_id, bezeichnung, gueltigkeit_von, gueltigkeit_bis,
             gefahrenanalyse, ccp_liste, ueberwachung, korrekturen, verifizierung, aktiv)
        VALUES (:id, :tid, :bez, :gv, :gb, :ga::jsonb, :ccp::jsonb,
                :ue::jsonb, :ko::jsonb, :ver::jsonb, TRUE)
    """), {
        "id": plan_id, "tid": tenant_id,
        "bez": body.get("bezeichnung", ""),
        "gv": body.get("gueltigkeit_von") or str(date.today()),
        "gb": body.get("gueltigkeit_bis"),
        "ga": json.dumps(body.get("gefahrenanalyse", [])),
        "ccp": json.dumps(body.get("ccp_liste", [])),
        "ue": json.dumps(body.get("ueberwachung", [])),
        "ko": json.dumps(body.get("korrekturen", [])),
        "ver": json.dumps(body.get("verifizierung", {})),
    })
    db.commit()
    return {"id": plan_id, "ok": True}


@router.patch("/haccp-plaene/{plan_id}", response_model=dict[str, Any], summary="HACCP-Plan aktualisieren")
def update_haccp_plan(
    plan_id: str,
    body: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    import json
    fields = []
    params: dict[str, Any] = {"id": plan_id, "tid": tenant_id}
    for col in ("bezeichnung", "gueltigkeit_von", "gueltigkeit_bis", "aktiv"):
        if col in body:
            fields.append(f"{col} = :{col}")
            params[col] = body[col]
    for col in ("gefahrenanalyse", "ccp_liste", "ueberwachung", "korrekturen", "verifizierung"):
        if col in body:
            fields.append(f"{col} = :{col}::jsonb")
            params[col] = json.dumps(body[col])
    if not fields:
        raise HTTPException(status_code=422, detail="Keine Felder zum Aktualisieren")
    db.execute(
        text(f"UPDATE domain_shared.futtermittel_haccp_plaene SET {', '.join(fields)} WHERE id = :id AND tenant_id = :tid"),
        params,
    )
    db.commit()
    return {"id": plan_id, "ok": True}


# ── VLOG-Meldungen ────────────────────────────────────────────────────────────

@router.get("/vlog-meldungen", response_model=list[dict[str, Any]], summary="VLOG-Meldungen auflisten")
def list_vlog_meldungen(
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM domain_shared.futtermittel_vlog_meldungen WHERE tenant_id = :tid"
    params: dict[str, Any] = {"tid": tenant_id}
    if status:
        sql += " AND status = :status"
        params["status"] = status
    sql += " ORDER BY meldedatum DESC LIMIT :limit"
    params["limit"] = limit
    try:
        rows = db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.post("/vlog-meldungen", response_model=dict[str, Any], status_code=201, summary="VLOG-Meldung erstellen")
def create_vlog_meldung(
    body: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    import uuid, json
    from datetime import date
    meldung_id = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO domain_shared.futtermittel_vlog_meldungen
            (id, tenant_id, rezeptur_id, meldedatum, menge_kg,
             rohstoff_liste, gvo_frei, zertifikat_nr, status, notiz)
        VALUES (:id, :tid, :rez, :md, :kg,
                :rl::jsonb, :gvo, :zert, 'erstellt', :notiz)
    """), {
        "id": meldung_id, "tid": tenant_id,
        "rez": body.get("rezeptur_id"),
        "md": body.get("meldedatum") or str(date.today()),
        "kg": body.get("menge_kg", 0),
        "rl": json.dumps(body.get("rohstoff_liste", [])),
        "gvo": body.get("gvo_frei", True),
        "zert": body.get("zertifikat_nr"),
        "notiz": body.get("notiz"),
    })
    db.commit()
    return {"id": meldung_id, "ok": True}


@router.patch("/vlog-meldungen/{meldung_id}/status", response_model=dict[str, Any], summary="VLOG-Meldung Status setzen")
def set_vlog_status(
    meldung_id: str,
    body: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    neuer_status = body.get("status")
    if neuer_status not in ("erstellt", "gesendet", "bestaetigt", "abgelehnt"):
        raise HTTPException(status_code=422, detail="Ungueltiger Status")
    db.execute(
        text("UPDATE domain_shared.futtermittel_vlog_meldungen SET status = :s WHERE id = :id AND tenant_id = :tid"),
        {"s": neuer_status, "id": meldung_id, "tid": tenant_id},
    )
    db.commit()
    return {"id": meldung_id, "status": neuer_status}


# ── QS-Leitfaden-Pruefpunkte ──────────────────────────────────────────────────

@router.get("/leitfaden-pruefpunkte", response_model=list[dict[str, Any]], summary="QS-Leitfaden-Pruefpunkte auflisten")
def list_pruefpunkte(
    periode: str | None = Query(None, description="YYYY-MM oder YYYY"),
    bestaetigt: bool | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM domain_shared.futtermittel_qs_pruefpunkte WHERE tenant_id = :tid"
    params: dict[str, Any] = {"tid": tenant_id}
    if periode:
        sql += " AND periode = :periode"
        params["periode"] = periode
    if bestaetigt is not None:
        sql += " AND bestaetigt = :bestaetigt"
        params["bestaetigt"] = bestaetigt
    sql += " ORDER BY kategorie, punkt_nr LIMIT :limit"
    params["limit"] = limit
    try:
        rows = db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.post("/leitfaden-pruefpunkte", response_model=dict[str, Any], status_code=201, summary="QS-Pruefpunkt anlegen")
def create_pruefpunkt(
    body: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    import uuid
    punkt_id = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO domain_shared.futtermittel_qs_pruefpunkte
            (id, tenant_id, periode, kategorie, punkt_nr, bezeichnung,
             anforderung, bestaetigt, abweichung, massnahme)
        VALUES (:id, :tid, :per, :kat, :pnr, :bez,
                :anf, FALSE, NULL, NULL)
    """), {
        "id": punkt_id, "tid": tenant_id,
        "per": body.get("periode", ""),
        "kat": body.get("kategorie", "allgemein"),
        "pnr": body.get("punkt_nr", ""),
        "bez": body.get("bezeichnung", ""),
        "anf": body.get("anforderung", ""),
    })
    db.commit()
    return {"id": punkt_id, "ok": True}


@router.post("/leitfaden-pruefpunkte/{punkt_id}/bestaetigen", response_model=dict[str, Any], summary="QS-Pruefpunkt bestaetigen")
def bestaetigen_pruefpunkt(
    punkt_id: str,
    body: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(_tenant),
) -> dict[str, Any]:
    db.execute(text("""
        UPDATE domain_shared.futtermittel_qs_pruefpunkte
        SET bestaetigt = TRUE,
            abweichung = :abw,
            massnahme  = :mas,
            bestaetigt_am = NOW(),
            bestaetigt_von = :von
        WHERE id = :id AND tenant_id = :tid
    """), {
        "abw": body.get("abweichung"),
        "mas": body.get("massnahme"),
        "von": body.get("bestaetigt_von"),
        "id": punkt_id, "tid": tenant_id,
    })
    db.commit()
    return {"id": punkt_id, "bestaetigt": True}
