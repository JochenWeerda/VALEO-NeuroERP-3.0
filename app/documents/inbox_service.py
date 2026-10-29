"""Liest die vorhandene DMS-Inbox und den Dokumentspeicher. Schreibt keine Belege."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.services.business_partner_service import BusinessPartnerService
from app.services.whatsapp_intake_service import WhatsAppIntakeService

from .inbox_contract import (
    PIPELINE_GAPS,
    build_queue_item,
    extract_line_items,
    match_values,
)

logger = logging.getLogger(__name__)


def _row_mapping(row: Any) -> dict[str, Any]:
    mapping = row._mapping
    created = mapping.get("created_at")
    return {
        "id": mapping.get("id"),
        "dms_document_id": mapping.get("dms_document_id"),
        "dms_url": mapping.get("dms_url"),
        "ocr_text": mapping.get("ocr_text"),
        "parsed_fields": mapping.get("parsed_fields") or {},
        "confidence": mapping.get("confidence") or 0.0,
        "status": mapping.get("status"),
        "created_at": created.isoformat() if hasattr(created, "isoformat") else created,
    }


def load_pending_entries(
    db: Session,
    tenant_id: str,
    *,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], bool]:
    """Nur Eintraege des Request-Mandanten (nie Query-Parameter als Quelle)."""
    try:
        rows = db.execute(
            text(
                """
                SELECT id, dms_document_id, dms_url, ocr_text, parsed_fields,
                       confidence, status, created_at
                FROM domain_shared.dms_inbox
                WHERE status = 'pending'
                  AND tenant_id = :tenant_id
                ORDER BY created_at DESC NULLS LAST
                LIMIT :limit
                """
            ),
            {"tenant_id": tenant_id, "limit": limit},
        ).fetchall()
        return [_row_mapping(row) for row in rows], True
    except Exception as exc:  # noqa: BLE001 — Tabelle oder Schema kann fehlen
        logger.warning("DMS-Inbox nicht lesbar: %s", exc)
        db.rollback()
        return [], False


def load_entry(db: Session, tenant_id: str, item_id: str) -> dict[str, Any] | None:
    try:
        row = db.execute(
            text(
                """
                SELECT id, dms_document_id, dms_url, ocr_text, parsed_fields,
                       confidence, status, created_at
                FROM domain_shared.dms_inbox
                WHERE id = :item_id
                  AND tenant_id = :tenant_id
                """
            ),
            {"item_id": item_id, "tenant_id": tenant_id},
        ).fetchone()
        return _row_mapping(row) if row else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("DMS-Inbox-Eintrag nicht lesbar: %s", exc)
        db.rollback()
        return None


def load_duplicate_candidates(
    db: Session,
    tenant_id: str,
    numbers: list[str],
) -> list[dict[str, Any]]:
    needles = [n.strip() for n in numbers if n and n.strip()]
    if not needles:
        return []
    try:
        stmt = text(
            """
            SELECT id, doc_type, doc_number
            FROM documents
            WHERE data->>'tenantId' = :tenant_id
              AND (doc_number IN :numbers OR data->>'number' IN :numbers)
            LIMIT 50
            """
        ).bindparams(bindparam("numbers", expanding=True))
        rows = db.execute(stmt, {"tenant_id": tenant_id, "numbers": needles}).fetchall()
        return [
            {
                "id": str(row.id) if row.id is not None else None,
                "doc_type": row.doc_type,
                "doc_number": row.doc_number,
            }
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Dokumentspeicher fuer Dubletten nicht lesbar: %s", exc)
        db.rollback()
        return []


def load_contract_candidates(
    db: Session,
    tenant_id: str,
    *,
    contract_number: str | None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Read-only Kontrakt-Treffer (Kon + Agrar) — kein Schreibzugriff."""
    needle = (contract_number or "").strip() or None
    if not needle:
        return []
    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(
        *,
        contract_id: str | None,
        number: str | None,
        source: str,
        matched_by: str,
    ) -> None:
        cid = (contract_id or "").strip()
        if not cid or cid in seen:
            return
        seen.add(cid)
        found.append({
            "contract_id": cid,
            "contract_number": number,
            "source": source,
            "matched_by": matched_by,
        })

    try:
        kon_rows = db.execute(
            text(
                """
                SELECT contract_id, contract_no
                FROM domain_ops.kon_contract
                WHERE tenant_id = :tenant_id
                  AND (contract_no = :needle OR contract_id = :needle)
                LIMIT :limit
                """
            ),
            {"tenant_id": tenant_id, "needle": needle, "limit": limit},
        ).fetchall()
        for row in kon_rows:
            _add(
                contract_id=str(row.contract_id) if row.contract_id else None,
                number=str(row.contract_no) if row.contract_no else None,
                source="kon_contract",
                matched_by="contract_number",
            )
    except Exception as exc:  # noqa: BLE001 — Schema/Tabelle kann fehlen
        logger.warning("Kon-Kontrakte fuer Inbox nicht lesbar: %s", exc)
        db.rollback()

    if len(found) < limit:
        try:
            agrar_rows = db.execute(
                text(
                    """
                    SELECT id, contract_number
                    FROM domain_inventory.agrar_contracts
                    WHERE tenant_id = :tenant_id
                      AND (contract_number = :needle OR id = :needle)
                    LIMIT :limit
                    """
                ),
                {"tenant_id": tenant_id, "needle": needle, "limit": limit},
            ).fetchall()
            for row in agrar_rows:
                _add(
                    contract_id=str(row.id) if row.id else None,
                    number=str(row.contract_number) if row.contract_number else None,
                    source="agrar_contract",
                    matched_by="contract_number",
                )
                if len(found) >= limit:
                    break
        except Exception as exc:  # noqa: BLE001
            logger.warning("Agrar-Kontrakte fuer Inbox nicht lesbar: %s", exc)
            db.rollback()

    return found[:limit]


def load_supplier_candidates(
    db: Session,
    tenant_id: str,
    *,
    supplier_id: str | None,
    supplier_name: str | None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Read-only Lieferanten-Treffer ueber BusinessPartnerService — keine Buchung."""
    needle_id = (supplier_id or "").strip() or None
    needle_name = (supplier_name or "").strip() or None
    if not needle_id and not needle_name:
        return []
    try:
        service = BusinessPartnerService(db, tenant_id)
        found: list[dict[str, Any]] = []
        seen: set[str] = set()

        def _add(partner: Any, matched_by: str) -> None:
            if partner is None or not getattr(partner, "is_supplier", False):
                return
            partner_id = str(getattr(partner, "partner_id", "") or "")
            if not partner_id or partner_id in seen:
                return
            seen.add(partner_id)
            found.append({
                "partner_id": partner_id,
                "partner_number": getattr(partner, "partner_number", None),
                "name": getattr(partner, "name_1", None),
                "matched_by": matched_by,
            })

        if needle_id:
            by_number = service.repo.get_by_partner_number(needle_id)
            _add(by_number, "partner_number")
            by_pk = service.repo.get_by_id_or_none(needle_id)
            _add(by_pk, "partner_id")

        query = needle_id or needle_name
        if query and len(found) < limit:
            partners, _total = service.list_partners(
                query=query,
                is_supplier=True,
                limit=limit,
            )
            for partner in partners:
                _add(partner, "name_search")
                if len(found) >= limit:
                    break
        return found
    except Exception as exc:  # noqa: BLE001 — Stamm kann fehlen
        logger.warning("Lieferanten-Stammdaten fuer Inbox nicht lesbar: %s", exc)
        db.rollback()
        return []


def load_article_candidates_by_index(
    db: Session,
    tenant_id: str,
    parsed_fields: dict[str, Any] | None,
) -> dict[int, list[dict[str, Any]]]:
    """Artikel-Lookup nur fuer echte Positionszeilen — Muster WhatsAppIntakeService.match_artikel."""
    lines = extract_line_items(parsed_fields if isinstance(parsed_fields, dict) else {})
    if not lines:
        return {}
    try:
        service = WhatsAppIntakeService(db, tenant_id)
    except Exception as exc:  # noqa: BLE001 — Stamm kann fehlen
        logger.warning("Artikel-Stammdaten-Service fuer Inbox nicht initialisierbar: %s", exc)
        return {}
    by_index: dict[int, list[dict[str, Any]]] = {}
    for line in lines:
        index = int(line.get("index") or 0)
        needle = line.get("article_number") or line.get("name")
        try:
            hit = service.match_artikel(str(needle) if needle else None)
        except Exception as exc:  # noqa: BLE001 — Lookup best-effort
            logger.warning("Artikel-Lookup Inbox Zeile %s fehlgeschlagen: %s", index, exc)
            db.rollback()
            by_index[index] = []
            continue
        by_index[index] = [hit] if hit else []
    return by_index


def _enrich_queue_item(
    db: Session,
    tenant_id: str,
    entry: dict[str, Any],
    existing_documents: list[dict[str, Any]],
    nutzer: Any | None,
) -> dict[str, Any]:
    fields = entry.get("parsed_fields") or {}
    values = match_values(fields if isinstance(fields, dict) else {})
    partners = load_supplier_candidates(
        db,
        tenant_id,
        supplier_id=values.get("supplierId") or values.get("supplierNumber"),
        supplier_name=values.get("supplierName"),
    )
    contracts = load_contract_candidates(
        db,
        tenant_id,
        contract_number=values.get("contractId"),
    )
    articles = load_article_candidates_by_index(
        db,
        tenant_id,
        fields if isinstance(fields, dict) else {},
    )
    return build_queue_item(
        entry=entry,
        existing_documents=existing_documents,
        partner_candidates=partners,
        contract_candidates=contracts,
        article_candidates_by_index=articles,
        nutzer=nutzer,
    )


def build_queue(
    db: Session,
    tenant_id: str,
    nutzer: Any | None,
    *,
    limit: int = 50,
) -> dict[str, Any]:
    entries, available = load_pending_entries(db, tenant_id, limit=limit)
    numbers = []
    for entry in entries:
        fields = entry.get("parsed_fields") or {}
        number = fields.get("invoice_number") or fields.get("number")
        if number:
            numbers.append(str(number))
    existing = load_duplicate_candidates(db, tenant_id, numbers)
    items = [_enrich_queue_item(db, tenant_id, entry, existing, nutzer) for entry in entries]
    return {
        "ok": True,
        "source": "dms_inbox",
        "available": available,
        "booking_allowed": False,
        "count": len(items),
        "items": items,
        "gaps": list(PIPELINE_GAPS),
        "message": None if available else "DMS-Inbox nicht verfuegbar",
    }


def build_item(
    db: Session,
    tenant_id: str,
    item_id: str,
    nutzer: Any | None,
) -> dict[str, Any] | None:
    entry = load_entry(db, tenant_id, item_id)
    if entry is None:
        return None
    fields = entry.get("parsed_fields") or {}
    number = fields.get("invoice_number") or fields.get("number")
    existing = load_duplicate_candidates(db, tenant_id, [str(number)] if number else [])
    return _enrich_queue_item(db, tenant_id, entry, existing, nutzer)


def prepare_item(
    db: Session,
    tenant_id: str,
    item_id: str,
    nutzer: Any | None,
) -> dict[str, Any] | None:
    item = build_item(db, tenant_id, item_id, nutzer)
    if item is None:
        return None
    return {
        "ok": True,
        "booking_allowed": False,
        "item": item,
        "command": item["command"],
    }
