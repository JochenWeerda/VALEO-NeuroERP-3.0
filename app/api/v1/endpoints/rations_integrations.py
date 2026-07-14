"""Ration integrations: machine/lab imports and contract-gated herd-data sync."""
from __future__ import annotations
from datetime import datetime
import json
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.agrar.rations.control.feeding_control import LoadedComponent, compute_feeding_control
from app.agrar.rations.integrations.adapters import agrirouter_to_feeding_log, icar_ade_to_cow_profile, laboratory_to_feed_ingredient, payload_hash
from app.agrar.rations.integrations.herd_data import HerdDataKind, normalize_herd_data_bundle
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services.rations_herd_data_sync_service import HerdDataSyncBlocked, HerdDataSyncService

router = APIRouter(prefix="/integrations", tags=["rations-integrations"])
AdapterName = Literal["agrirouter", "icar-ade", "laboratory"]

class ImportBody(BaseModel):
    payload: dict[str, Any] = Field(description="Provider payload, decoded to JSON at the transport boundary")


class HerdDataConnectionIn(BaseModel):
    provider: Literal["ddw"] = "ddw"
    herd_id: str = Field(min_length=1, max_length=160)
    base_url: str = Field(min_length=8, max_length=500)
    endpoint_templates: dict[HerdDataKind, str]
    query_parameters: dict[HerdDataKind, str] = Field(default_factory=dict)
    credential_env_key: str = Field(default="DDW_HERD_DATA_TOKEN", min_length=3, max_length=80)
    contract_ref: str = Field(min_length=1, max_length=160)
    consent_ref: str = Field(min_length=1, max_length=160)
    enabled: bool = False
    live_enabled: bool = False

    @field_validator("endpoint_templates")
    @classmethod
    def validate_templates(cls, value: dict[HerdDataKind, str]) -> dict[HerdDataKind, str]:
        expected = {"group_kpi", "health_alert", "genetic_profile"}
        if set(value) != expected:
            raise ValueError("Endpoint-Templates fuer group_kpi, health_alert und genetic_profile sind erforderlich.")
        if any(not path.startswith("/") or "://" in path for path in value.values()):
            raise ValueError("Endpoint-Templates muessen relative Pfade sein.")
        return value


class HerdDataSyncRequest(BaseModel):
    updated_since: datetime | None = None


class HerdDataMockImport(BaseModel):
    connection_id: str = Field(min_length=1)
    kind: HerdDataKind
    payload: dict[str, Any]
    persist: bool = True

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

@router.post("/{adapter}/import", summary="Rationsdaten aus externem Standard importieren", response_model=dict)
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

@router.get("/imports", summary="Importjournal der Rationsschnittstellen", response_model=list[dict])
async def list_rations_imports(adapter: AdapterName | None = None, limit: int = Query(default=50, ge=1, le=250),
                               tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    rows = db.execute(text("""SELECT id,adapter,external_id,source_version,target_model,result,imported_at
      FROM domain_agrar.rations_integration_imports WHERE tenant_id=:tenant_id
        AND (:adapter IS NULL OR adapter=:adapter) ORDER BY imported_at DESC LIMIT :limit"""),
      {"tenant_id": tenant_id, "adapter": adapter, "limit": limit}).mappings().all()
    return [dict(row) for row in rows]


@router.post("/herd-data/connections", summary="Herd-Data-Verbindung anlegen/aktualisieren", response_model=dict)
async def upsert_herd_data_connection(body: HerdDataConnectionIn, tenant_id: str = Depends(get_tenant_id),
                                      db: Session = Depends(get_db)):
    row = db.execute(text("""INSERT INTO domain_agrar.herd_data_connections
      (id,tenant_id,provider,herd_id,base_url,endpoint_templates,query_parameters,credential_env_key,
       contract_ref,consent_ref,enabled,live_enabled)
      VALUES (:id,:tenant_id,:provider,:herd_id,:base_url,CAST(:endpoint_templates AS jsonb),
       CAST(:query_parameters AS jsonb),:credential_env_key,:contract_ref,:consent_ref,:enabled,:live_enabled)
      ON CONFLICT (tenant_id,provider,herd_id) DO UPDATE SET base_url=EXCLUDED.base_url,
       endpoint_templates=EXCLUDED.endpoint_templates,query_parameters=EXCLUDED.query_parameters,
       credential_env_key=EXCLUDED.credential_env_key,contract_ref=EXCLUDED.contract_ref,
       consent_ref=EXCLUDED.consent_ref,enabled=EXCLUDED.enabled,live_enabled=EXCLUDED.live_enabled,updated_at=now()
      RETURNING id,provider,herd_id,base_url,endpoint_templates,query_parameters,credential_env_key,
       contract_ref,consent_ref,enabled,live_enabled,created_at,updated_at"""), {
        "id": uuid7(), "tenant_id": tenant_id, **body.model_dump(exclude={"endpoint_templates", "query_parameters"}),
        "endpoint_templates": json.dumps(body.endpoint_templates), "query_parameters": json.dumps(body.query_parameters),
    }).mappings().first()
    db.commit()
    return dict(row)


@router.get("/herd-data/connections", summary="Herd-Data-Verbindungen auflisten", response_model=list[dict])
async def list_herd_data_connections(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    rows = db.execute(text("""SELECT id,provider,herd_id,base_url,endpoint_templates,query_parameters,
      credential_env_key,contract_ref,consent_ref,enabled,live_enabled,created_at,updated_at
      FROM domain_agrar.herd_data_connections WHERE tenant_id=:tenant_id ORDER BY provider,herd_id"""),
      {"tenant_id": tenant_id}).mappings().all()
    return [dict(row) for row in rows]


@router.post("/herd-data/connections/{connection_id}/sync", summary="Herd-Data-Delta-Sync ausfuehren", response_model=dict)
async def sync_herd_data_connection(connection_id: str, body: HerdDataSyncRequest,
                                    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    service = HerdDataSyncService(db)
    try:
        connection = service.load_connection(tenant_id=tenant_id, connection_id=connection_id)
        return await service.sync(connection, updated_since=body.updated_since)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Herd-Data-Verbindung nicht gefunden.") from exc
    except HerdDataSyncBlocked as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Herd-Data-Sync fehlgeschlagen: {exc}") from exc


@router.post("/herd-data/mock-import", summary="Herd-Data-Mockvertrag normalisieren", response_model=dict)
async def import_herd_data_mock(body: HerdDataMockImport, tenant_id: str = Depends(get_tenant_id),
                                db: Session = Depends(get_db)):
    service = HerdDataSyncService(db)
    try:
        connection = service.load_connection(tenant_id=tenant_id, connection_id=body.connection_id)
        observations = normalize_herd_data_bundle(body.kind, body.payload, provider=connection.provider)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Herd-Data-Verbindung nicht gefunden.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    imported = service.persist_observations(connection, observations) if body.persist else 0
    if body.persist:
        db.commit()
    return {"kind": body.kind, "normalized_count": len(observations), "imported_count": imported,
            "observations": [item.model_dump(mode="json") for item in observations]}


@router.get("/herd-data/observations", summary="Normalisierte Herd-Data-Beobachtungen", response_model=list[dict])
async def list_herd_data_observations(kind: HerdDataKind | None = None, herd_id: str | None = None,
                                      limit: int = Query(default=100, ge=1, le=500),
                                      tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    rows = db.execute(text("""SELECT id,provider,herd_id,kind,entity_id,effective_at,provider_updated_at,
      group_id,previous_group_id,is_deleted,payload,imported_at FROM domain_agrar.herd_data_observations
      WHERE tenant_id=:tenant_id AND (:kind IS NULL OR kind=:kind) AND (:herd_id IS NULL OR herd_id=:herd_id)
      ORDER BY effective_at DESC LIMIT :limit"""),
      {"tenant_id": tenant_id, "kind": kind, "herd_id": herd_id, "limit": limit}).mappings().all()
    return [dict(row) for row in rows]
