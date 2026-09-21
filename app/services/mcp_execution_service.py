"""Authenticated ERP adapters; a catalog entry alone never enables execution."""
from __future__ import annotations

from datetime import date
import hashlib
import json
from typing import Any, Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.crm_kontakt_service import CrmKontaktService
from app.services.mask_action_runtime_service import _write_audit
from app.services.mcp_tool_registry_service import mcp_tool_registry_service


class ToolExecutionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool_name: str
    parameters: dict[str, Any]
    mode: Literal["validate", "dryRun", "propose", "execute"] = "dryRun"
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=200)


class ContactLogInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kunden_nr: str = Field(min_length=1, max_length=20)
    kanal: Literal["telefon", "email", "besuch", "post"]
    ergebnis: str = Field(min_length=1, max_length=10000)
    wiedervorlage_datum: date | None = None


def execute_mcp_tool(db: Session, request: ToolExecutionRequest, user: dict, tenant_header: str | None) -> dict:
    """Use the verified identity, never a tenant or actor from tool arguments."""
    actor = user.get("sub")
    tenant = (user.get("raw") or {}).get("tenant_id")
    if not isinstance(actor, str) or not actor.strip() or not isinstance(tenant, str) or not tenant.strip():
        raise HTTPException(403, "Verified subject and tenant_id claims are required")
    if len(actor) > 120 or len(tenant) > 64:
        raise HTTPException(403, "Identity claims exceed the ERP field limits")
    if tenant_header is not None and tenant_header != tenant:
        raise HTTPException(403, "Tenant header does not match the verified token")
    try:
        tool = mcp_tool_registry_service.get_tool(request.tool_name)
    except KeyError as exc:
        raise HTTPException(404, "Unknown ERP tool") from exc
    if tool["scope"] not in user.get("scopes", []):
        raise HTTPException(403, "Required tool scope is missing")
    # Approval must come from a durable approval workflow, never a boolean argument.
    if tool.get("human_approval_required") or request.tool_name != "crm.contact.log":
        raise HTTPException(501, "No verified execution adapter is connected for this tool")
    try:
        contact = ContactLogInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid contact log parameters") from exc
    parameters = contact.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            # Serializes identical keys across processes, including the first call.
            lock_bytes = hashlib.sha256(json.dumps([tenant, request.tool_name, request.idempotency_key]).encode()).digest()[:8]
            db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})
            previous = db.execute(text("""
                SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
                WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
            """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key}).mappings().first()
            if previous:
                if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
                    raise HTTPException(409, "Idempotency key is already bound to another request")
                result = previous["result"]
                if isinstance(result, str):
                    result = json.loads(result)
                db.rollback()  # Release the transaction lock without another write.
                return {**result, "replayed": True}
        exists = db.execute(text("""SELECT 1 FROM public.kunden k
            JOIN domain_crm.business_partners bp ON bp.partner_id = CAST(k.business_partner_id AS text)
            WHERE k.kunden_nr=:customer AND bp.tenant_id=:tenant FOR SHARE OF k, bp"""),
                            {"customer": contact.kunden_nr, "tenant": tenant}).first()
        if not exists:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        # The existing UI service commits. A child Session confines that commit to
        # a SAVEPOINT so the contact, audit and replay record remain atomic.
        with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
            saved = CrmKontaktService(child, tenant).create({
                "kunden_nr": contact.kunden_nr, "art": contact.kanal,
                "notiz": contact.ergebnis, "wiedervorlage": parameters["wiedervorlage_datum"],
                "bediener": actor,
            })
        audit_id = _write_audit(db, tenant_id=tenant, action_key=request.tool_name,
                               entity_type="customer_contact", entity_id=saved["id"],
                               audit_reason="MCP contact log", idempotency_key=request.idempotency_key,
                               summary=f"Contact logged by {actor}")
        result = {"success": True, "mode": "execute", "replayed": False,
                  "kontakt_id": saved["id"], "erfasst_am": saved["created_at"], "auditEntryId": audit_id}
        db.execute(text("""
            INSERT INTO public.mcp_tool_executions
                (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
            VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
        """), {"tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key,
                 "actor": actor, "hash": fingerprint, "result": json.dumps(result)})
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc
