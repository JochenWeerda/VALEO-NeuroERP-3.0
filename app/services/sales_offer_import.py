"""Atomic, idempotent import of explicitly specified sales offers.

Seit 09.11.2026 (BELEG-052, DocFlow einziger Belegspeicher) entsteht je CSV-Zeile ein Angebotsentwurf in DocFlow
statt einer Zeile in ``domain_crm.sales_offers``. Die CSV kennt nur Kopfdaten; der Betrag steht als eine
Pauschalposition (Menge 1, Preis = Betrag, ohne Steuerschluessel) im Entwurf. Vor der Freigabe wird das Angebot in
der Belegmaske vervollstaendigt - ohne Steuerschluessel bucht nichts. ``valid_until`` fuehrt DocFlow nicht.
"""
from __future__ import annotations

import csv
import hashlib
import io
import math
import json
import re
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from app.core.business_time import business_now
from app.core.identity_context import current_identity
from app.domains.shared.events import IntegrationEvent
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.services.mask_action_runtime_service import _write_audit

TOOL = "sales.offer.import_csv.v1"
HEADERS = ("offer_number", "subject", "customer_id", "total_amount", "currency", "valid_until")


def parse_offer_csv(content: str) -> list[dict]:
    if len(content.encode("utf-8")) > 1048576:
        raise HTTPException(413, "CSV exceeds 1 MB")
    try:
        reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff"), newline=""), delimiter=";", strict=True)
        headers = reader.fieldnames or []
        if len(set(headers)) != len(headers) or not set(HEADERS[:5]).issubset(headers) or not set(headers).issubset(HEADERS):
            raise HTTPException(422, "Required CSV headers: " + ";".join(HEADERS[:5]) + "; optional: valid_until")
        result, numbers = [], set()
        for row in reader:
            if len(result) >= 1000:
                raise HTTPException(422, "CSV exceeds 1000 rows")
            if None in row or any(value is None for value in row.values()):
                raise HTTPException(422, f"Invalid CSV row {reader.line_num}")
            row = {key: value.strip() for key, value in row.items()}
            row.setdefault("valid_until", "")
            number, subject = row["offer_number"], row["subject"]
            if not row["customer_id"]:
                raise HTTPException(422, f"Customer reference required at row {reader.line_num}")
            if not number or len(number) > 64 or not subject or len(subject) > 255:
                raise HTTPException(422, f"Offer number and subject required at row {reader.line_num}")
            if number in numbers:
                raise HTTPException(422, f"Duplicate offer number at row {reader.line_num}")
            numbers.add(number)
            try:
                amount = Decimal(row["total_amount"])
                if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
                    raise ValueError()
                if not math.isfinite(float(amount)):
                    raise ValueError()
                valid_until = datetime.fromisoformat(row["valid_until"]) if row["valid_until"] else None
            except (InvalidOperation, ValueError):
                raise HTTPException(422, f"Invalid amount or date at row {reader.line_num}")
            if not re.fullmatch(r"[A-Z]{3}", row["currency"]):
                raise HTTPException(422, f"Invalid currency at row {reader.line_num}")
            result.append({**row,
                           "total_amount": float(amount), "valid_until": valid_until})
        if not result:
            raise HTTPException(422, "CSV contains no offers")
        return result
    except csv.Error as error:
        raise HTTPException(422, "Malformed CSV") from error


QUELLE = "csv_import"


def persist_offer(db, tenant: str, row: dict, actor: str) -> str:
    """Ein Angebotsentwurf in DocFlow; dieselbe Angebotsnummer je Mandant nur einmal (409)."""
    from app.services.beleg_anlage import Position, lege_beleg_an

    nummer = row["offer_number"]
    if db.execute(text("SELECT 1 FROM domain_docflow.document_headers WHERE tenant_id = :t AND doc_type = 'sales_offer' "
                       "AND source_system = :q AND source_ref = :n"), {"t": tenant, "q": QUELLE, "n": nummer}).first():
        raise HTTPException(409, f"Offer number {nummer} already imported")
    kunde = db.execute(text("SELECT id::text FROM domain_crm.customers WHERE tenant_id = :t AND (id::text = :k OR "
                            "customer_number = :k) LIMIT 1"), {"t": tenant, "k": row["customer_id"]}).scalar()
    if kunde is None:
        raise HTTPException(422, f"Unknown customer for offer {nummer}")
    return lege_beleg_an(
        db, tenant, "sales_offer", partner_id=kunde, quelle=QUELLE, referenz=nummer, entwurf_nr=f"CSV-{nummer}",
        akteur=actor, positionen=[Position(artikel_nr="PAUSCHAL", bezeichnung=row["subject"][:255], menge=1,
                                           einheit="Stk", einzelpreis=float(row["total_amount"]))])


def _persist_all(db, tenant: str, rows: list[dict], actor: str) -> list[str]:
    """Alle Entwuerfe in einer Einheit: DocFlow committet je Beleg; im Savepoint gibt das nur den Savepoint frei,
    erst ``import_offers`` committet. Scheitert die zweite Zeile, ist auch die erste nicht angelegt."""
    from sqlalchemy.orm import Session

    if not isinstance(db, Session):  # schlanke Test-Adapter
        return [persist_offer(db, tenant, row, actor) for row in rows]
    with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as inner:
        ids = [persist_offer(inner, tenant, row, actor) for row in rows]
        inner.commit()
    return ids


def import_offers(db, tenant: str, content: str, key: str, reason: str | None):
    principal = current_identity()
    if principal.tenant_id != tenant or principal.claims.get("identity_type") != "human" or principal.claims.get("act") or principal.claims.get("agent_id") or not principal.subject:
        raise HTTPException(403, "Import requires an authorized human identity")
    rows = parse_offer_csv(content)
    if any(row["currency"] != "EUR" for row in rows):
        raise HTTPException(422, "Only EUR offers can be imported")
    fingerprint = hashlib.sha256(json.dumps([content, reason], ensure_ascii=False).encode()).hexdigest()
    lock = int.from_bytes(hashlib.sha256(json.dumps([tenant, TOOL, key]).encode()).digest()[:8], "big", signed=True)
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock})
        previous = db.execute(text("SELECT actor_id,payload_hash,result FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key"), {"tenant": tenant, "tool": TOOL, "key": key}).mappings().first()
        if previous:
            if previous["actor_id"] != principal.subject or previous["payload_hash"] != fingerprint:
                raise HTTPException(409, "Idempotency key belongs to another command")
            result = previous["result"]
            if isinstance(result, str): result = json.loads(result)
            db.commit()
            return {**result, "replayed": True}
        # Stable lock order avoids deadlocks between overlapping imports.
        offer_ids = _persist_all(db, tenant, sorted(rows, key=lambda r: r["offer_number"]), principal.subject)
        batch_id, now = str(uuid4()), business_now()
        audit_id = _write_audit(db, tenant_id=tenant, action_key=TOOL, entity_type="sales_offer_import", entity_id=batch_id, audit_reason=reason, idempotency_key=key, summary=f"Imported {len(offer_ids)} sales offers", performed_by=principal.subject)
        event = IntegrationEvent(aggregate_id=batch_id, timestamp=now, event_type=TOOL, tenant_id=tenant, payload={"offer_ids": offer_ids, "actor_id": principal.subject, "audit_id": audit_id})
        db.add(OutboxEvent(id=event.event_id, event_type=event.event_type, aggregate_id=batch_id, tenant_id=tenant, timestamp=now, payload=json.dumps(asdict(event), default=str), published=False))
        result = {"success": True, "count": len(offer_ids), "offer_ids": offer_ids, "auditEntryId": audit_id}
        db.execute(text("INSERT INTO public.mcp_tool_executions (tenant_id,tool_name,idempotency_key,actor_id,payload_hash,result) VALUES (:tenant,:tool,:key,:actor,:hash,CAST(:result AS jsonb))"), {"tenant": tenant, "tool": TOOL, "key": key, "actor": principal.subject, "hash": fingerprint, "result": json.dumps(result)})
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(503, "Import failed; no changes confirmed") from error
