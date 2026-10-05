"""Authenticated ERP adapters; a catalog entry alone never enables execution."""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any, Literal
from uuid import uuid4

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


class InvoiceProposeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    lieferschein_nr: str = Field(min_length=1, max_length=40)
    rechnungsdatum: date


_BILLABLE_DELIVERY_STATUSES = ("posted", "printed", "gebucht")


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
    # A catalog flag or a client boolean never posts. Only an explicit adapter may write.
    if request.tool_name == "crm.contact.log":
        return _log_contact(db, request, actor, tenant)
    if request.tool_name == "sales.invoice.propose":
        return _propose_invoice(db, request, actor, tenant)
    raise HTTPException(501, "No verified execution adapter is connected for this tool")


def _log_contact(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
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


def _money(totals: Any, key: str) -> float:
    if isinstance(totals, str):
        totals = json.loads(totals)
    if not isinstance(totals, dict) or totals.get(key) is None:
        raise HTTPException(409, "Delivery note has no stored totals")
    return round(float(totals[key]), 2)


def _propose_invoice(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Store a pending invoice proposal. This call never posts an invoice."""
    try:
        invoice = InvoiceProposeInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid invoice proposal parameters") from exc
    if request.mode == "execute":
        raise HTTPException(501, "Invoice posting is not an MCP execution")
    parameters = invoice.model_dump(mode="json")
    if request.mode == "propose" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "propose requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "propose":
            lock_bytes = hashlib.sha256(
                json.dumps([tenant, request.tool_name, request.idempotency_key]).encode()
            ).digest()[:8]
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
                db.rollback()
                return {**result, "replayed": True}
        note = db.execute(text("""
            SELECT n.id, n.status, n.totals,
                   (SELECT COUNT(*) FROM domain_sales.delivery_note_positions p
                    WHERE p.delivery_note_id = n.id) AS positionen
            FROM domain_sales.delivery_notes n
            WHERE n.tenant_id=:tenant AND n.delivery_note_number=:nr
            FOR SHARE OF n
        """), {"tenant": tenant, "nr": invoice.lieferschein_nr}).mappings().first()
        if not note:
            raise HTTPException(404, "Delivery note not found in the authenticated tenant")
        if note["status"] not in _BILLABLE_DELIVERY_STATUSES:
            raise HTTPException(409, "Delivery note is not ready to invoice")
        preview = {
            "betrag_netto": _money(note["totals"], "netto"),
            "mwst": _money(note["totals"], "mwst"),
            "positionen": int(note["positionen"] or 0),
        }
        if request.mode != "propose":
            return {"success": True, "mode": request.mode, "posted": False, **preview}
        proposal_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        db.execute(text("""
            INSERT INTO public.agent_proposals
                (proposal_id, tenant_id, action_type, risk_level, approval_status,
                 context_snapshot, rationale, idempotency_key, created_at)
            VALUES
                (:id, :tenant, 'rechnung_vorschlag', 'high', 'pending',
                 CAST(:snapshot AS json), :rationale, :key, :now)
        """), {
            "id": proposal_id,
            "tenant": tenant,
            "snapshot": json.dumps({
                "context_summary": f"Lieferschein {invoice.lieferschein_nr}",
                "proposed_action": "Rechnung vorschlagen, nicht buchen",
                "human_approval_required": True,
                "audit_events": [{"event": "proposal_created", "occurred_at": now}],
                "lieferschein_nr": invoice.lieferschein_nr,
                "rechnungsdatum": parameters["rechnungsdatum"],
                "actor_id": actor,
                "payload_hash": fingerprint,
                **preview,
            }),
            "rationale": "MCP sales.invoice.propose",
            "key": hashlib.sha256(f"{tenant}|{request.tool_name}|{request.idempotency_key}".encode()).hexdigest(),
            "now": now,
        })
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="sales_invoice_proposal", entity_id=proposal_id,
            audit_reason="MCP invoice proposal", idempotency_key=request.idempotency_key,
            summary=f"Invoice proposal for {invoice.lieferschein_nr} by {actor}",
        )
        result = {
            "success": True, "mode": "propose", "replayed": False, "posted": False,
            "entwurf_id": proposal_id, "approval_status": "pending", "auditEntryId": audit_id,
            **preview,
        }
        db.execute(text("""
            INSERT INTO public.mcp_tool_executions
                (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
            VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
        """), {
            "tenant": tenant, "tool": request.tool_name, "key": request.idempotency_key,
            "actor": actor, "hash": fingerprint, "result": json.dumps(result),
        })
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc
