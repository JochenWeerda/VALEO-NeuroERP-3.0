"""Ration integration imports: agrirouter 2.0, ICAR ADE and laboratory JSON."""
from __future__ import annotations
import json
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.agrar.rations.control.feeding_control import LoadedComponent, compute_feeding_control
from app.agrar.rations.integrations.adapters import agrirouter_to_feeding_log, icar_ade_to_cow_profile, laboratory_to_feed_ingredient, payload_hash
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/integrations", tags=["rations-integrations"])
AdapterName = Literal["agrirouter", "icar-ade", "laboratory"]

class ImportBody(BaseModel):
    payload: dict[str, Any] = Field(description="Provider payload, decoded to JSON at the transport boundary")

_ADAPTERS = {"agrirouter": agrirouter_to_feeding_log, "icar-ade": icar_ade_to_cow_profile, "laboratory": laboratory_to_feed_ingredient}

def _existing(db: Session, tenant_id: str, adapter: str, external_id: str) -> dict[str, Any] | None:
    row = db.execute(text("""SELECT id, adapter, external_id, source_version, target_model, result, imported_at
      FROM domain_agrar.rations_integration_imports WHERE tenant_id=:tenant_id AND adapter=:adapter AND external_id=:external_id"""),
      {"tenant_id": tenant_id, "adapter": adapter, "external_id": external_id}).mappings().first()
    return dict(row) if row else None

def _persist_feeding_log(db: Session, tenant_id: str, mapped: dict[str, Any]) -> dict[str, Any]:
    target = mapped["target"]
    components = [LoadedComponent(c["feed_id"], c["name"], float(c["soll_kg"]), float(c["ist_kg"])) for c in target["komponenten"]]
    control = compute_feeding_control(components, float(target.get("restfutter_kg") or 0), int(target["tierzahl"]), float(target["tm_pct"]),
        milch_kg_kuh=target.get("milch_kg_kuh"), milchpreis_eur_kg=target.get("milchpreis_eur_kg"),
        futterkosten_eur_kuh=target.get("futterkosten_eur_kuh"), futtertisch_temp_c=target.get("futtertisch_temp_c"),
        umgebung_temp_c=target.get("umgebung_temp_c"))
    result = control.to_dict()
    db.execute(text("""INSERT INTO domain_agrar.feeding_logs
      (id,tenant_id,group_id,feeding_date,ration_ref,payload,control_result)
      VALUES (:id,:tenant_id,:group_id,:feeding_date,:ration_ref,CAST(:payload AS jsonb),CAST(:result AS jsonb))
      ON CONFLICT (tenant_id,group_id,feeding_date) DO UPDATE SET ration_ref=EXCLUDED.ration_ref,
        payload=EXCLUDED.payload,control_result=EXCLUDED.control_result,created_at=now()"""),
      {"id": uuid7(), "tenant_id": tenant_id, "group_id": target["group_id"], "feeding_date": target["feeding_date"],
       "ration_ref": target.get("ration_ref"), "payload": json.dumps(target, ensure_ascii=False), "result": json.dumps(result, ensure_ascii=False)})
    return result

@router.post("/{adapter}/import", summary="Rationsdaten aus externem Standard importieren")
async def import_rations_data(adapter: AdapterName, body: ImportBody, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        mapped = _ADAPTERS[adapter](body.payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    external_id = str(mapped["external_id"])
    existing = _existing(db, tenant_id, adapter, external_id)
    if existing:
        existing["duplicate"] = True
        return existing
    if adapter == "agrirouter":
        mapped["feeding_control"] = _persist_feeding_log(db, tenant_id, mapped)
    row = db.execute(text("""INSERT INTO domain_agrar.rations_integration_imports
      (id,tenant_id,adapter,external_id,source_version,payload_hash,target_model,result)
      VALUES (:id,:tenant_id,:adapter,:external_id,:source_version,:payload_hash,:target_model,CAST(:result AS jsonb))
      RETURNING id,adapter,external_id,source_version,target_model,result,imported_at"""),
      {"id": uuid7(), "tenant_id": tenant_id, "adapter": adapter, "external_id": external_id,
       "source_version": mapped.get("source_version"), "payload_hash": payload_hash(body.payload),
       "target_model": mapped["target_model"], "result": json.dumps(mapped, ensure_ascii=False)}).mappings().first()
    db.commit()
    output = dict(row)
    output["duplicate"] = False
    return output

@router.get("/imports", summary="Importjournal der Rationsschnittstellen")
async def list_rations_imports(adapter: AdapterName | None = None, limit: int = Query(default=50, ge=1, le=250),
                               tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    rows = db.execute(text("""SELECT id,adapter,external_id,source_version,target_model,result,imported_at
      FROM domain_agrar.rations_integration_imports WHERE tenant_id=:tenant_id
        AND (:adapter IS NULL OR adapter=:adapter) ORDER BY imported_at DESC LIMIT :limit"""),
      {"tenant_id": tenant_id, "adapter": adapter, "limit": limit}).mappings().all()
    return [dict(row) for row in rows]