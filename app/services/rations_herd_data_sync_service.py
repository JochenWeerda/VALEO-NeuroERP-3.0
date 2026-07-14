"""Contract-gated daily delta sync for external dairy herd-data APIs."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Awaitable, Callable
from urllib.parse import urljoin

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.integrations.adapters import payload_hash
from app.agrar.rations.integrations.herd_data import (
    HerdDataKind,
    HerdDataObservation,
    normalize_herd_data_bundle,
)
from app.core.outbound_security import validate_outbound_http_target_against_allowlists
from app.core.uuid7 import uuid7

_ENV_KEY = re.compile(r"^[A-Z][A-Z0-9_]{2,80}$")
Transport = Callable[[str, dict[str, str], dict[str, str]], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class HerdDataConnection:
    id: str
    tenant_id: str
    provider: str
    herd_id: str
    base_url: str
    endpoint_templates: dict[str, str]
    query_parameters: dict[str, str]
    credential_env_key: str
    contract_ref: str
    consent_ref: str
    enabled: bool
    live_enabled: bool


class HerdDataSyncBlocked(RuntimeError):
    pass


def connection_from_row(row: dict[str, Any]) -> HerdDataConnection:
    def obj(value: Any) -> dict[str, str]:
        if isinstance(value, str):
            value = json.loads(value)
        return {str(k): str(v) for k, v in (value or {}).items()}

    return HerdDataConnection(
        id=str(row["id"]), tenant_id=str(row["tenant_id"]), provider=str(row["provider"]),
        herd_id=str(row["herd_id"]), base_url=str(row["base_url"]),
        endpoint_templates=obj(row.get("endpoint_templates")),
        query_parameters=obj(row.get("query_parameters")),
        credential_env_key=str(row.get("credential_env_key") or "DDW_HERD_DATA_TOKEN"),
        contract_ref=str(row.get("contract_ref") or ""), consent_ref=str(row.get("consent_ref") or ""),
        enabled=bool(row.get("enabled")), live_enabled=bool(row.get("live_enabled")),
    )


def validate_connection_for_live(connection: HerdDataConnection) -> tuple[str, str]:
    if not connection.enabled or not connection.live_enabled:
        raise HerdDataSyncBlocked("Herd-Data-Live-Sync ist fuer diese Verbindung nicht freigegeben.")
    if not connection.contract_ref or not connection.consent_ref:
        raise HerdDataSyncBlocked("Vertrags- und Einwilligungsreferenz sind fuer Live-Sync erforderlich.")
    if not _ENV_KEY.fullmatch(connection.credential_env_key):
        raise HerdDataSyncBlocked("credential_env_key verletzt den erlaubten ENV-Schluesselvertrag.")
    token = os.getenv(connection.credential_env_key, "").strip()
    if not token:
        raise HerdDataSyncBlocked(f"Credential-Secret fehlt: {connection.credential_env_key}")
    if set(connection.endpoint_templates) != {"group_kpi", "health_alert", "genetic_profile"}:
        raise HerdDataSyncBlocked("Alle drei vertraglich gelieferten Endpoint-Templates sind erforderlich.")
    allowed_domains = [v.strip() for v in os.getenv("HERD_DATA_ALLOWED_DOMAINS", "dairydatawarehouse.com").split(",") if v.strip()]
    base_url = validate_outbound_http_target_against_allowlists(
        connection.base_url, allowed_domains=allowed_domains, allowed_schemes=("https",)
    )
    return base_url.rstrip("/") + "/", token


async def _http_transport(url: str, headers: dict[str, str], params: dict[str, str]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Herd-Data-API muss ein JSON-Objekt liefern.")
    return payload


class HerdDataSyncService:
    def __init__(self, db: Session, transport: Transport | None = None):
        self.db = db
        self.transport = transport or _http_transport

    def load_connection(self, *, tenant_id: str, connection_id: str) -> HerdDataConnection:
        row = self.db.execute(text("""SELECT * FROM domain_agrar.herd_data_connections
          WHERE tenant_id=:tenant_id AND id=:id"""), {"tenant_id": tenant_id, "id": connection_id}).mappings().first()
        if not row:
            raise KeyError(connection_id)
        return connection_from_row(dict(row))

    def last_cursor(self, connection_id: str) -> datetime:
        value = self.db.execute(text("""SELECT cursor_to FROM domain_agrar.herd_data_sync_runs
          WHERE connection_id=:id AND status='success' ORDER BY finished_at DESC LIMIT 1"""), {"id": connection_id}).scalar()
        return value or datetime.now(timezone.utc) - timedelta(days=2)

    async def fetch_delta(self, connection: HerdDataConnection, *, updated_since: datetime) -> list[HerdDataObservation]:
        base_url, token = validate_connection_for_live(connection)
        observations: list[HerdDataObservation] = []
        for kind in ("group_kpi", "health_alert", "genetic_profile"):
            template = connection.endpoint_templates[kind]
            if not template.startswith("/") or "://" in template:
                raise HerdDataSyncBlocked(f"Endpoint-Template muss ein relativer Pfad sein: {kind}")
            url = urljoin(base_url, template.format(herd_id=connection.herd_id).lstrip("/"))
            validate_outbound_http_target_against_allowlists(
                url,
                allowed_domains=[v.strip() for v in os.getenv("HERD_DATA_ALLOWED_DOMAINS", "dairydatawarehouse.com").split(",") if v.strip()],
                allowed_schemes=("https",),
            )
            parameter = connection.query_parameters.get(kind)
            params = {parameter: (date.today().isoformat() if kind == "group_kpi" else updated_since.isoformat())} if parameter else {}
            payload = await self.transport(url, {"Authorization": f"Bearer {token}", "Accept": "application/json"}, params)
            observations.extend(normalize_herd_data_bundle(kind, payload, provider=connection.provider))
        return observations

    def persist_observations(self, connection: HerdDataConnection, observations: list[HerdDataObservation]) -> int:
        for observation in observations:
            raw = observation.model_dump(mode="json")
            self.db.execute(text("""INSERT INTO domain_agrar.herd_data_observations
              (id,tenant_id,connection_id,provider,herd_id,kind,entity_id,effective_at,provider_updated_at,
               group_id,previous_group_id,is_deleted,payload,payload_hash)
              VALUES (:id,:tenant_id,:connection_id,:provider,:herd_id,:kind,:entity_id,:effective_at,:provider_updated_at,
               :group_id,:previous_group_id,:is_deleted,CAST(:payload AS jsonb),:payload_hash)
              ON CONFLICT (tenant_id,provider,herd_id,kind,entity_id,effective_at) DO UPDATE SET
               provider_updated_at=EXCLUDED.provider_updated_at,group_id=EXCLUDED.group_id,
               previous_group_id=EXCLUDED.previous_group_id,is_deleted=EXCLUDED.is_deleted,
               payload=EXCLUDED.payload,payload_hash=EXCLUDED.payload_hash,imported_at=now()"""), {
                "id": uuid7(), "tenant_id": connection.tenant_id, "connection_id": connection.id,
                "provider": observation.provider, "herd_id": observation.herd_id, "kind": observation.kind,
                "entity_id": observation.entity_id, "effective_at": observation.effective_at,
                "provider_updated_at": observation.provider_updated_at, "group_id": observation.group_id,
                "previous_group_id": observation.previous_group_id, "is_deleted": observation.deleted,
                "payload": json.dumps(raw["payload"], ensure_ascii=False), "payload_hash": payload_hash(raw["payload"]),
            })
        return len(observations)

    async def sync(self, connection: HerdDataConnection, *, updated_since: datetime | None = None) -> dict[str, Any]:
        cursor_from = updated_since or self.last_cursor(connection.id)
        run_id = uuid7()
        self.db.execute(text("""INSERT INTO domain_agrar.herd_data_sync_runs
          (id,tenant_id,connection_id,status,cursor_from) VALUES (:id,:tenant_id,:connection_id,'running',:cursor_from)"""),
          {"id": run_id, "tenant_id": connection.tenant_id, "connection_id": connection.id, "cursor_from": cursor_from})
        try:
            observations = await self.fetch_delta(connection, updated_since=cursor_from)
            imported = self.persist_observations(connection, observations)
            cursor_to = max((item.provider_updated_at for item in observations), default=datetime.now(timezone.utc))
            self.db.execute(text("""UPDATE domain_agrar.herd_data_sync_runs SET status='success',cursor_to=:cursor_to,
              imported_count=:count,finished_at=now() WHERE id=:id"""), {"cursor_to": cursor_to, "count": imported, "id": run_id})
            self.db.commit()
            return {"run_id": run_id, "status": "success", "cursor_from": cursor_from, "cursor_to": cursor_to, "imported_count": imported}
        except Exception as exc:
            self.db.rollback()
            self.db.execute(text("""INSERT INTO domain_agrar.herd_data_sync_runs
              (id,tenant_id,connection_id,status,cursor_from,error,finished_at)
              VALUES (:id,:tenant_id,:connection_id,'failed',:cursor_from,:error,now())"""),
              {"id": uuid7(), "tenant_id": connection.tenant_id, "connection_id": connection.id,
               "cursor_from": cursor_from, "error": str(exc)[:1000]})
            self.db.commit()
            raise
