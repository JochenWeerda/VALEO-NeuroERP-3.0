"""Atomic, actor/content-bound DocFlow creation using existing replay storage."""
from __future__ import annotations
import json
from typing import Any
from uuid import NAMESPACE_URL, uuid5, uuid4
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import text
from app.core.exceptions import ConflictError, ValidationFailedError


def create_snapshot(service: Any, payload: Any) -> dict[str, Any]:
    key = payload.idempotency_key
    if key is not None and (not isinstance(key, str) or not 8 <= len(key.strip()) <= 120):
        raise ValidationFailedError('Ein gueltiger Idempotenzschluessel ist erforderlich.')
    if key and not service.akteur:
        raise ValidationFailedError('Ein gepruefter Akteur ist erforderlich.')
    content = payload.model_dump(mode='json', exclude={'idempotency_key', 'created_by'})
    if getattr(payload, 'screen_context', None) is None:
        content.pop('screen_context', None)  # Keep hashes of pre-provenance requests stable.
    content['actor'] = service.akteur
    resource = str(uuid5(NAMESPACE_URL, json.dumps([service.tenant_id, key])))
    try:
        if key:
            # No row exists yet: a transaction-scoped lock serializes this tenant/key.
            service.db.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:scope, 0))'),
                               {'scope': 'docflow.create:' + resource})
            cached = service.load_idempotent_response('create', resource, key, content)
            if cached:
                service.db.rollback()
                return cached
            if service.load_create_idempotency(key):
                raise ConflictError('Alter Auftrag ohne Inhaltsnachweis; neuer Schluessel erforderlich.')
        if payload.doc_type == 'sales_invoice':
            service._assert_invoice_customer_allowed(payload.customer_id)
        from app.services.docflow_screen_provenance import resolve_screen_context
        context = resolve_screen_context(getattr(payload, 'screen_context', None), payload.doc_type, service.tenant_id)
        if context is not None:
            from app.services.docflow_creation_context import validate_partner
            validate_partner(service.db, service.tenant_id, payload)
        doc_id = _apply_create(service, payload, context)
        snapshot = json.loads(json.dumps({'header': service.fetch_header(doc_id),
            'items': service.fetch_items(doc_id), 'pos_compliance': service.fetch_pos_compliance(doc_id),
            'screen_context': context}, default=str))
        service.upsert_outbox_event('docflow.document.created', doc_id, {
            'tenant_id': service.tenant_id, 'doc_id': doc_id, 'actor': service.akteur,
            'version': snapshot['header']['version'], 'idempotency_key': key})
        if key:
            service.store_create_idempotency(key, doc_id)
            service.store_idempotent_response('create', resource, key, snapshot, content)
        service.db.commit()
        return snapshot
    except BaseException:
        service.db.rollback()
        raise


def _apply_create(self: Any, payload: Any, context=None) -> str:
    from app.services.docflow_service import _money, steuerrichtung
    if payload.status in {"posted", "reversed", "cancelled"}:
        raise ValidationFailedError(
            f"Ein Beleg wird nicht im Status {payload.status} angelegt; gebucht und storniert wird über die Kommandos."
        )
    now = datetime.now(timezone.utc)
    doc_id = str(uuid4())
    self._kommando("create")
    total_net, total_tax, total_gross = Decimal("0"), Decimal("0"), Decimal("0")
    self.db.execute(
        text("""
            INSERT INTO domain_docflow.document_headers
            (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
             currency, total_net, total_tax, total_gross, document_date, posting_date, version, created_by, updated_by, created_at, updated_at)
            VALUES (:id, :tenant_id, :doc_type, :doc_number, :status, :source_system, :source_ref, :customer_id, :supplier_id,
             :currency, :total_net, :total_tax, :total_gross, :document_date, :posting_date, 1, :created_by, :updated_by, NOW(), NOW())
        """),
        {
            "id": doc_id, "tenant_id": self.tenant_id, "doc_type": payload.doc_type,
            "doc_number": payload.doc_number, "status": payload.status,
            "source_system": payload.source_system or "docflow.ui",
            "source_ref": payload.source_ref, "customer_id": payload.customer_id,
            "supplier_id": payload.supplier_id, "currency": payload.currency,
            "total_net": _money(total_net), "total_tax": _money(total_tax), "total_gross": _money(total_gross),
            "document_date": payload.document_date or now,
            "posting_date": payload.posting_date,
            "created_by": self._wer(payload.created_by), "updated_by": self._wer(payload.created_by),
        },
    )
    total_net, total_tax, total_gross = self._insert_items(doc_id, payload.items, steuerrichtung(payload.doc_type))
    self.db.execute(
        text("UPDATE domain_docflow.document_headers SET total_net=:n, total_tax=:t, total_gross=:g WHERE id=:id AND tenant_id=:tenant_id"),
        {"id": doc_id, "tenant_id": self.tenant_id, "n": _money(total_net), "t": _money(total_tax), "g": _money(total_gross)},
    )
    self.upsert_pos_compliance(doc_id, payload.pos_compliance)
    self._protokolliere("create", doc_id, {"doc_type": payload.doc_type, "doc_number": payload.doc_number,
                                           "status": payload.status, "screen_context": context})
    self.best_effort_audit("docflow_create", "docflow_document", doc_id,
                           {"doc_type": payload.doc_type, "doc_number": payload.doc_number, "status": payload.status})
    return doc_id
