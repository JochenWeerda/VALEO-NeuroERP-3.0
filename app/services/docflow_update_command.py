"""Versioned, replay-safe DocFlow editing in the existing document transaction."""
from __future__ import annotations
import json
from typing import Any
from sqlalchemy import text
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError


def update_document(service: Any, doc_id: str, payload: Any) -> dict[str, Any]:
    version = getattr(payload, 'expected_version', None)
    key = getattr(payload, 'idempotency_key', None)
    if type(version) is not int or version < 1:
        raise ValidationFailedError('Eine positive expected_version ist erforderlich.')
    if not isinstance(key, str) or not 8 <= len(key.strip()) <= 120:
        raise ValidationFailedError('Ein gueltiger Idempotenzschluessel ist erforderlich.')
    if not service.akteur:
        raise ValidationFailedError('Ein gepruefter Akteur ist erforderlich.')
    content = payload.model_dump(mode='json', exclude={'idempotency_key', 'updated_by'})
    content['actor'] = service.akteur
    try:
        service._sperre(doc_id)
        cached = service.load_idempotent_response('update', doc_id, key, content)
        if cached:
            service.db.rollback()
            return cached
        _apply_update(service, doc_id, payload)
        snapshot = {
            'header': service.fetch_header(doc_id),
            'items': service.fetch_items(doc_id),
            'pos_compliance': service.fetch_pos_compliance(doc_id),
        }
        # Stored and live results must use the same JSON-safe snapshot, including dates/Decimals.
        snapshot = json.loads(json.dumps(snapshot, default=str))
        service.upsert_outbox_event('docflow.document.updated', doc_id, {
            'tenant_id': service.tenant_id, 'doc_id': doc_id,
            'version': snapshot['header']['version'], 'actor': service.akteur,
            'idempotency_key': key,
        })
        service.store_idempotent_response('update', doc_id, key, snapshot, content)
        service.db.commit()
        return snapshot
    except BaseException:
        service.db.rollback()
        raise


def _apply_update(self, doc_id: str, payload: Any) -> None:
    from app.services.docflow_service import _money, steuerrichtung
    header = self.fetch_header(doc_id)
    if not header:
        raise EntityNotFoundError("DocflowDocument", doc_id)
    effective_doc_type = str(header.get("doc_type") or "")
    if effective_doc_type == "sales_invoice":
        effective_customer_id = (
            payload.customer_id if payload.customer_id is not None else header.get("customer_id")
        )
        self._assert_invoice_customer_allowed(effective_customer_id)
    if int(header.get("version") or 1) != payload.expected_version:
        raise ConflictError("Version conflict")
    if str(header.get("status")) in {"posted", "reversed", "cancelled"}:
        raise ConflictError("Posted/Reversed/Cancelled document cannot be edited")
    current_status = str(header.get("status") or "draft")
    if payload.items is not None and current_status != "draft":
        raise ValidationFailedError("Positionen kÃ¶nnen nur im Status Entwurf (draft) ersetzt werden")
    if payload.status in {"posted", "reversed"}:
        raise ValidationFailedError(
            f"Der Status {payload.status} wird nicht gesetzt, sondern entsteht durch Buchen bzw. Stornieren."
        )
    if payload.status is not None and payload.status != current_status:
        raise ValidationFailedError("Statuswechsel erfolgen ausschliesslich ueber die Fachkommandos.")
    self._kommando("update")
    updates: dict[str, Any] = {"id": doc_id, "tenant_id": self.tenant_id, "updated_by": self._wer(payload.updated_by)}
    set_parts = ["updated_at = NOW()", "version = version + 1", "updated_by = :updated_by"]
    for field in ("status", "customer_id", "source_system", "source_ref", "supplier_id", "currency", "document_date", "posting_date"):
        val = getattr(payload, field, None)
        if val is not None:
            set_parts.append(f"{field} = :{field}")
            updates[field] = val
    self.db.execute(
        text(f"UPDATE domain_docflow.document_headers SET {', '.join(set_parts)} WHERE id = :id AND tenant_id = :tenant_id"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        updates,
    )
    if payload.items is not None:
        self.db.execute(
            text("DELETE FROM domain_docflow.document_items WHERE tenant_id = :tenant_id AND header_id = :header_id"),
            {"tenant_id": self.tenant_id, "header_id": doc_id},
        )
        total_net, total_tax, total_gross = self._insert_items(doc_id, payload.items, steuerrichtung(effective_doc_type))
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET total_net=:n, total_tax=:t, total_gross=:g WHERE id=:id AND tenant_id=:tenant_id"),
            {"id": doc_id, "tenant_id": self.tenant_id, "n": _money(total_net), "t": _money(total_tax), "g": _money(total_gross)},
        )
    self.upsert_pos_compliance(doc_id, payload.pos_compliance)
    self._protokolliere("update", doc_id, {"felder": sorted(k for k in updates if k not in ("id", "tenant_id", "updated_by")),
                                           "positionen_ersetzt": payload.items is not None, "idempotency_key": payload.idempotency_key,
                                           "expected_version": payload.expected_version})
    self.best_effort_audit("docflow_update", "docflow_document", doc_id, {"updated_by": self._wer(payload.updated_by)})
