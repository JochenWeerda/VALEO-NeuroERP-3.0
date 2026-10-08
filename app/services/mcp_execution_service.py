"""Authenticated ERP adapters; a catalog entry alone never enables execution."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
from typing import Any, Literal
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.crm_kontakt_service import CrmKontaktService
from app.services.document_allocation_service import LineToRegister
from app.services.mask_action_runtime_service import _write_audit
from app.services.mcp_tool_registry_service import mcp_tool_registry_service
from app.services.sales_invoice_service import (
    InvoiceCreationError,
    SalesInvoiceService,
    SourceLine,
)


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


class ActivityCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    kunden_nr: str = Field(min_length=1, max_length=20)
    betreff: str = Field(min_length=1, max_length=200)
    typ: Literal["Anruf", "Besuch", "E-Mail", "Aufgabe", "Meeting", "Sonstiges"]
    datum: date | None = None
    notiz: str | None = Field(default=None, max_length=10000)
    verantwortlich: str | None = Field(default=None, max_length=100)


class InvoiceProposeInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    lieferschein_nr: str = Field(min_length=1, max_length=40)
    rechnungsdatum: date


class InvoicePostInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    proposal_id: str = Field(min_length=1, max_length=36)


_BILLABLE_DELIVERY_STATUSES = ("posted", "printed", "gebucht")


def _tenant_from_claims(raw: object) -> str | None:
    """Mandanten-ID nur aus verifiziertem Token — nie aus Tool-Parametern.

    Akzeptiert ``tenant_id`` (kanonisch) und ``mandanten_id`` (Alias in manchen
    IdP-Claims). Ein Client-Parameter ``mandanten_id`` bleibt durch
    ``extra=forbid`` abgewiesen.
    """
    if not isinstance(raw, dict):
        return None
    for key in ("tenant_id", "mandanten_id"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _customer_in_tenant(db: Session, *, kunden_nr: str, tenant: str) -> dict | None:
    """Operativer CRM-Stamm des authentifizierten Mandanten (kein Cross-Tenant-Fallback)."""
    return db.execute(text("""
        SELECT id::text AS id, company_name AS name, customer_number AS kunden_nr
        FROM domain_crm.customers
        WHERE tenant_id::text = :tenant
          AND (customer_number = :customer OR id::text = :customer)
        FOR SHARE
    """), {"customer": kunden_nr, "tenant": tenant}).mappings().first()


def execute_mcp_tool(db: Session, request: ToolExecutionRequest, user: dict, tenant_header: str | None) -> dict:
    """Use the verified identity, never a tenant or actor from tool arguments."""
    actor = user.get("sub")
    tenant = _tenant_from_claims(user.get("raw"))
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
    if request.tool_name == "crm.activity.create":
        return _create_activity(db, request, actor, tenant)
    if request.tool_name == "sales.invoice.propose":
        return _propose_invoice(db, request, actor, tenant)
    if request.tool_name == "sales.invoice.post":
        return _post_invoice(db, request, actor, tenant)
    raise HTTPException(501, "No verified execution adapter is connected for this tool")


def _advisory_lock(db: Session, tenant: str, tool_name: str, idempotency_key: str) -> None:
    lock_bytes = hashlib.sha256(json.dumps([tenant, tool_name, idempotency_key]).encode()).digest()[:8]
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": int.from_bytes(lock_bytes, "big", signed=True)})


def _replay_or_none(db: Session, tenant: str, tool_name: str, key: str, actor: str, fingerprint: str) -> dict | None:
    previous = db.execute(text("""
        SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
        WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
    """), {"tenant": tenant, "tool": tool_name, "key": key}).mappings().first()
    if not previous:
        return None
    if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
        raise HTTPException(409, "Idempotency key is already bound to another request")
    result = previous["result"]
    if isinstance(result, str):
        result = json.loads(result)
    db.rollback()
    return {**result, "replayed": True}


def _store_execution(
    db: Session, *, tenant: str, tool: str, key: str, actor: str, fingerprint: str, result: dict
) -> None:
    db.execute(text("""
        INSERT INTO public.mcp_tool_executions
            (tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result)
        VALUES (:tenant, :tool, :key, :actor, :hash, CAST(:result AS jsonb))
    """), {
        "tenant": tenant, "tool": tool, "key": key, "actor": actor,
        "hash": fingerprint, "result": json.dumps(result),
    })


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


def _create_activity(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    try:
        activity = ActivityCreateInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid activity parameters") from exc
    parameters = activity.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        customer = _customer_in_tenant(db, kunden_nr=activity.kunden_nr, tenant=tenant)
        if not customer:
            raise HTTPException(404, "Customer not found in the authenticated tenant")
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "proposedChanges": parameters}
        activity_id = str(uuid4())
        now = datetime.now(timezone.utc)
        verantwortlich = (activity.verantwortlich or actor)[:100]
        db.execute(text("""
            INSERT INTO domain_crm.activities
              (id, type, title, customer, contact_person, date, status, assigned_to, description, tenant_id)
            VALUES
              (:aid, :typ, :titel, :kunde, :person, :datum, 'offen', :verantwortlich, :notiz, :tid)
        """), {
            "aid": activity_id,
            "typ": activity.typ[:20],
            "titel": activity.betreff[:200],
            "kunde": str(customer["name"] or customer["kunden_nr"] or activity.kunden_nr)[:100],
            "person": verantwortlich,
            "datum": parameters["datum"] or now.date().isoformat(),
            "verantwortlich": verantwortlich,
            "notiz": activity.notiz,
            "tid": tenant,
        })
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="crm_activity", entity_id=activity_id,
            audit_reason="MCP activity create", idempotency_key=request.idempotency_key,
            summary=f"Activity '{activity.betreff}' by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False,
            "activity_id": activity_id, "erfasst_am": now.isoformat(), "auditEntryId": audit_id,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc


def _invoice_sources_from_positions(ls_id: str, positions: list[dict]) -> list[SourceLine]:
    sources: list[SourceLine] = []
    for pos in positions:
        zeile = LineToRegister.from_mapping(pos)
        if not zeile.line_id or not zeile.unit:
            continue
        sources.append(SourceLine(
            document_type="delivery_note",
            document_id=ls_id,
            line_id=zeile.line_id,
            article_id=zeile.article_id,
            article_number=pos.get("artikel_nr"),
            description=pos.get("bezeichnung"),
            quantity=Decimal(str(zeile.quantity or 0)),
            unit=str(zeile.unit),
            unit_price=Decimal(str(pos.get("netto_preis") or 0)),
            vat_rate=(
                Decimal(str(pos["mwst_prozent"]))
                if pos.get("mwst_prozent") is not None
                else None
            ),
        ))
    return sources


def _post_invoice(db: Session, request: ToolExecutionRequest, actor: str, tenant: str) -> dict:
    """Create a sales invoice draft from an approved proposal. Never skips human approval."""
    try:
        payload = InvoicePostInput.model_validate(request.parameters)
    except ValidationError as exc:
        raise HTTPException(422, "Invalid invoice post parameters") from exc
    if request.mode == "propose":
        raise HTTPException(422, "sales.invoice.post does not accept propose; use sales.invoice.propose")
    parameters = payload.model_dump(mode="json")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    fingerprint = hashlib.sha256(json.dumps(parameters, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        if request.mode == "execute":
            _advisory_lock(db, tenant, request.tool_name, request.idempotency_key)  # type: ignore[arg-type]
            replayed = _replay_or_none(
                db, tenant, request.tool_name, request.idempotency_key, actor, fingerprint  # type: ignore[arg-type]
            )
            if replayed is not None:
                return replayed
        proposal = db.execute(text("""
            SELECT proposal_id, action_type, approval_status, risk_level,
                   context_snapshot, execution_result
            FROM public.agent_proposals
            WHERE proposal_id=:id AND tenant_id=:tenant
            FOR UPDATE OF agent_proposals
        """), {"id": payload.proposal_id, "tenant": tenant}).mappings().first()
        if not proposal:
            raise HTTPException(404, "Proposal not found in the authenticated tenant")
        if proposal["action_type"] != "rechnung_vorschlag":
            raise HTTPException(409, "Proposal is not an invoice proposal")
        if proposal["approval_status"] != "approved":
            raise HTTPException(409, "Proposal is not approved")
        if proposal["execution_result"] is not None:
            existing = proposal["execution_result"]
            if isinstance(existing, str):
                existing = json.loads(existing)
            if isinstance(existing, dict) and existing.get("invoice_id"):
                if request.mode != "execute":
                    return {
                        "success": True, "mode": request.mode, "posted": False,
                        "already_executed": True,
                        **{k: existing[k] for k in ("invoice_id", "invoice_number", "status") if k in existing},
                    }
                raise HTTPException(409, "Proposal was already executed")
        snapshot = proposal["context_snapshot"] or {}
        if isinstance(snapshot, str):
            snapshot = json.loads(snapshot)
        if not isinstance(snapshot, dict):
            raise HTTPException(409, "Proposal snapshot is unusable")
        lieferschein_nr = snapshot.get("lieferschein_nr")
        rechnungsdatum_raw = snapshot.get("rechnungsdatum")
        if not isinstance(lieferschein_nr, str) or not lieferschein_nr.strip():
            raise HTTPException(409, "Proposal snapshot lacks lieferschein_nr")
        try:
            rechnungsdatum = date.fromisoformat(str(rechnungsdatum_raw))
        except (TypeError, ValueError) as exc:
            raise HTTPException(409, "Proposal snapshot lacks a valid rechnungsdatum") from exc
        preview = {
            "proposal_id": payload.proposal_id,
            "lieferschein_nr": lieferschein_nr,
            "rechnungsdatum": rechnungsdatum.isoformat(),
            "betrag_netto": snapshot.get("betrag_netto"),
            "mwst": snapshot.get("mwst"),
            "positionen": snapshot.get("positionen"),
        }
        if request.mode != "execute":
            return {"success": True, "mode": request.mode, "posted": False, **preview}
        note = db.execute(text("""
            SELECT n.id, n.status, n.customer_id, n.delivery_note_number
            FROM domain_sales.delivery_notes n
            WHERE n.tenant_id=:tenant AND n.delivery_note_number=:nr
            FOR UPDATE OF n
        """), {"tenant": tenant, "nr": lieferschein_nr}).mappings().first()
        if not note:
            raise HTTPException(404, "Delivery note not found in the authenticated tenant")
        if note["status"] not in _BILLABLE_DELIVERY_STATUSES:
            raise HTTPException(409, "Delivery note is not ready to invoice")
        positions = [
            dict(row) for row in db.execute(text("""
                SELECT * FROM domain_sales.delivery_note_positions
                WHERE delivery_note_id = :id ORDER BY pos_nr
            """), {"id": note["id"]}).mappings().all()
        ]
        sources = _invoice_sources_from_positions(str(note["id"]), positions)
        invoice_number = f"RE-{note['delivery_note_number'] or str(note['id'])[:8]}"
        try:
            with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as child:
                ergebnis = SalesInvoiceService(child, tenant).create_from_sources(
                    invoice_number=invoice_number,
                    customer_id=str(note.get("customer_id") or ""),
                    invoice_date=rechnungsdatum,
                    sources=sources,
                    reason="rechnung_aus_lieferschein_mcp",
                    user_id=actor,
                    note=f"MCP post from proposal {payload.proposal_id}",
                )
        except InvoiceCreationError as exc:
            raise HTTPException(409, str(exc)) from exc
        invoice_id = str(ergebnis.invoice.id)
        db.execute(text("""
            UPDATE domain_sales.delivery_notes
            SET status = 'invoiced', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant
        """), {"id": note["id"], "tenant": tenant})
        execution_result = {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "status": "entwurf",
            "executed_by": actor,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        db.execute(text("""
            UPDATE public.agent_proposals
            SET execution_result = CAST(:result AS json)
            WHERE proposal_id = :id AND tenant_id = :tenant
        """), {"result": json.dumps(execution_result), "id": payload.proposal_id, "tenant": tenant})
        audit_id = _write_audit(
            db, tenant_id=tenant, action_key=request.tool_name,
            entity_type="sales_invoice", entity_id=invoice_id,
            audit_reason="MCP invoice post from approved proposal",
            idempotency_key=request.idempotency_key,
            summary=f"Invoice {invoice_number} from proposal {payload.proposal_id} by {actor}",
        )
        result = {
            "success": True, "mode": "execute", "replayed": False, "posted": False,
            "invoice_id": invoice_id, "invoice_number": invoice_number, "status": "entwurf",
            "proposal_id": payload.proposal_id, "auditEntryId": audit_id,
            "fibu_journal": False,
        }
        _store_execution(
            db, tenant=tenant, tool=request.tool_name, key=request.idempotency_key,  # type: ignore[arg-type]
            actor=actor, fingerprint=fingerprint, result=result,
        )
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "ERP tool transaction failed; no success confirmed") from exc
