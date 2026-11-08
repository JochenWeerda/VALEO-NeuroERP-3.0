"""Versioned count-sheet creation shared by REST, UI, CLI and MCP.

The revision covers every source value used by the existing batch builder.
The caller owns commit/rollback for the business row, audit, outbox and replay.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.betrieb_roles import LAGER_SCHREIBEN
from app.core.identity_context import current_identity
from app.services.command_idempotency import lock_and_replay, store_execution
from app.services.inventory_auxiliary_service import InventoryAuxiliaryService
from app.services.mask_action_runtime_service import _write_audit, _write_outbox

COMMAND = "inventory.count_sheet.create.v1"
SCREEN = "lager/inventur-nebenlaeufe"
ACTION = "create_count_sheet"
ENDPOINT = "/api/v1/inventory/auxiliary/actions/create_count_sheet"


class CountSheetCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    inventory_count_id: str = Field(min_length=1, max_length=120)
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=5, max_length=500)

    @field_validator("inventory_count_id", "idempotency_key", "reason")
    @classmethod
    def canonical_nonblank(cls, value: str) -> str:
        if value != value.strip() or not value.strip():
            raise ValueError("Nichtleerer Wert ohne Randabstand erforderlich")
        return value


def _principal(tenant: str, *, write: bool):
    principal = current_identity()
    if (principal.tenant_id != tenant or not principal.subject
            or not principal.roles.intersection(LAGER_SCHREIBEN)):
        raise HTTPException(403, "Inventur-Schreibrolle und gepruefter Mandant erforderlich")
    identity_type = principal.claims.get("identity_type")
    if principal.claims.get("act") or (identity_type == "human" and principal.claims.get("agent_id")):
        raise HTTPException(403, "Delegierte Identitaet ist nicht freigeschaltet")
    if identity_type not in {"human", "agent", "service"}:
        raise HTTPException(403, "Deklarierter Identitaetstyp erforderlich")
    if write and identity_type != "human":
        from app.services.mcp_write_capability import authorize_agent
        authorize_agent(principal, COMMAND, ENDPOINT, SCREEN, ACTION)
    return principal


# Exactly the fields used by InventoryAuxiliaryService.create, with explicit
# order. JSONB textual output supplies a canonical, server-produced snapshot.
_SNAPSHOT = text("""
    SELECT jsonb_build_object(
      'id', c.id, 'warehouse_id', c.warehouse_id, 'status', c.status,
      'lines', COALESCE((
        SELECT jsonb_agg(jsonb_build_object(
          'line_id', l.id, 'article_id', l.article_id, 'expected_qty', l.expected_qty,
          'counted_qty', l.counted_qty, 'difference', COALESCE(l.counted_qty,0)-COALESCE(l.expected_qty,0),
          'batch_number', l.batch_number, 'warehouse_id', COALESCE(l.warehouse_id,c.warehouse_id),
          'unit_value', COALESCE(a.purchase_price,0)) ORDER BY l.article_id, l.id)
        FROM domain_inventory.inventory_count_lines l
        JOIN domain_inventory.articles a ON a.id=l.article_id AND a.tenant_id=:tenant
        WHERE l.inventory_count_id=c.id AND l.tenant_id=:tenant
      ), '[]'::jsonb)
    )::text AS snapshot,
    (SELECT COUNT(*) FROM domain_inventory.inventory_count_lines l
      JOIN domain_inventory.articles a ON a.id=l.article_id AND a.tenant_id=:tenant
      WHERE l.inventory_count_id=c.id AND l.tenant_id=:tenant) AS line_count
    FROM domain_inventory.inventory_counts c WHERE c.tenant_id=:tenant AND c.id=:id
""")


def snapshot(db: Session, tenant: str, count_id: str) -> dict[str, Any]:
    """Return a revision, not the raw inventory or pricing data."""
    _principal(tenant, write=False)
    if not isinstance(count_id, str) or not count_id.strip() or count_id != count_id.strip():
        raise HTTPException(422, "Inventurkennung erforderlich")
    row = db.execute(_SNAPSHOT, {"tenant": tenant, "id": count_id}).mappings().first()
    if row is None:
        raise HTTPException(404, "Inventur nicht gefunden")
    return {"inventory_count_id": count_id, "revision": hashlib.sha256(row["snapshot"].encode("utf-8")).hexdigest(),
            "line_count": row["line_count"]}


def _lock_sources(db: Session, tenant: str, count_id: str) -> None:
    params = {"tenant": tenant, "id": count_id}
    # The parent lock also blocks FK-checked insertion of new count lines.
    parent = db.execute(text("SELECT id FROM domain_inventory.inventory_counts "
                             "WHERE tenant_id=:tenant AND id=:id FOR UPDATE"), params).first()
    if parent is None:
        raise HTTPException(404, "Inventur nicht gefunden")
    db.execute(text("SELECT id FROM domain_inventory.inventory_count_lines "
                    "WHERE tenant_id=:tenant AND inventory_count_id=:id ORDER BY id FOR UPDATE"), params).all()
    db.execute(text("SELECT a.id FROM domain_inventory.articles a WHERE a.tenant_id=:tenant AND EXISTS "
                    "(SELECT 1 FROM domain_inventory.inventory_count_lines l WHERE l.tenant_id=:tenant "
                    "AND l.inventory_count_id=:id AND l.article_id=a.id) ORDER BY a.id FOR SHARE"), params).all()


def create_count_sheet(db: Session, tenant: str, command: CountSheetCommand) -> dict[str, Any]:
    principal = _principal(tenant, write=True)
    actor = principal.subject
    fingerprint = hashlib.sha256(json.dumps(command.model_dump(exclude={"idempotency_key"}),
                                            sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    replay = lock_and_replay(db, tenant=tenant, command=COMMAND, key=command.idempotency_key,
                             actor=actor, fingerprint=fingerprint)
    if replay is not None:
        return replay
    _lock_sources(db, tenant, command.inventory_count_id)
    current = snapshot(db, tenant, command.inventory_count_id)
    if current["revision"] != command.expected_revision:
        raise HTTPException(409, "Inventurstand geaendert; bitte neu laden")
    created = InventoryAuxiliaryService(db, tenant).create(
        count_id=command.inventory_count_id, batch_type="count_sheet", actor=actor,
        reason=command.reason, commit=False)
    audit_id = _write_audit(db, tenant_id=tenant, action_key=COMMAND, entity_type="inventory_auxiliary_batch",
                            entity_id=str(created["id"]), audit_reason=command.reason,
                            idempotency_key=command.idempotency_key,
                            summary="Zaehlliste wiederverwendet" if created.get("duplicate") else "Zaehlliste erstellt",
                            performed_by=actor)
    correlation = str(uuid4())
    outbox_id = _write_outbox(db, tenant_id=tenant,
                              event_type="inventory.count_sheet.reused.v1" if created.get("duplicate") else COMMAND,
                              aggregate_id=str(created["id"]),
                              payload={"inventory_count_id": command.inventory_count_id, "actor_id": actor,
                                       "audit_id": audit_id, "correlation_id": correlation})
    result = {"success": True, "id": str(created["id"]), "status": created["status"],
              "source_hash": created["source_hash"], "duplicate": bool(created.get("duplicate")),
              "auditEntryId": audit_id, "outboxEventId": outbox_id, "replayed": False}
    store_execution(db, tenant=tenant, command=COMMAND, key=command.idempotency_key,
                    actor=actor, fingerprint=fingerprint, result=result)
    return result
