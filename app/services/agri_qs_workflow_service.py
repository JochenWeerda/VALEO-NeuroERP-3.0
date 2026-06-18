"""WM-AGRI-QS-003: QS-Workflow fuer Silo-Lots mit Audit-Rueckkopplung."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.supply_chain_event_service import SupplyChainEventService


class AgriQsWorkflowError(ValueError):
    """Fachlicher Fehler im QS-Workflow."""


_ALLOWED_QS_STATUS = frozenset({"in_pruefung", "frei", "gesperrt", "reserviert", "reinigung"})
_LOT_STATUS_BY_QS = {
    "in_pruefung": "in_pruefung",
    "frei": "active",
    "gesperrt": "gesperrt",
    "reserviert": "reserviert",
    "reinigung": "reinigung",
}


class AgriQsWorkflowService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def change_lot_qs_status(
        self,
        *,
        lot_id: str,
        target_status: str,
        reason: str,
        operator: str,
        sample_id: str | None = None,
        analysis_id: str | None = None,
        lab_document_id: str | None = None,
        gmp_evidence_id: str | None = None,
        vlog_evidence_id: str | None = None,
        production_release_ref: str | None = None,
    ) -> dict[str, Any]:
        target = target_status.strip()
        if target not in _ALLOWED_QS_STATUS:
            raise AgriQsWorkflowError("qs_status ungueltig")
        if not reason.strip():
            raise AgriQsWorkflowError("QS-Grund ist erforderlich")
        if not operator.strip():
            raise AgriQsWorkflowError("QS-Bediener ist erforderlich")
        if target == "frei" and not any((sample_id, analysis_id, lab_document_id)):
            raise AgriQsWorkflowError("QS-Freigabe benoetigt Probe, Analyse oder Labordokument")

        lot = self.db.execute(
            text("""
                SELECT id, virtual_lot_number, source_ticket_id, article_id,
                       quantity_tons, status
                FROM domain_inventory.silo_lots
                WHERE (id::text = :lot_id OR virtual_lot_number = :lot_id)
                  AND tenant_id = :tenant_id
                LIMIT 1
            """),
            {"lot_id": lot_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not lot:
            raise AgriQsWorkflowError("Silo-Lot nicht gefunden")
        lot_d = dict(lot)
        previous_status = str(lot_d.get("status") or "")
        target_lot_status = _LOT_STATUS_BY_QS[target]

        self.db.execute(
            text("""
                UPDATE domain_inventory.silo_lots
                SET status = :target_status,
                    updated_at = now()
                WHERE id = :lot_id AND tenant_id = :tenant_id
            """),
            {
                "target_status": target_lot_status,
                "lot_id": lot_d["id"],
                "tenant_id": self.tenant_id,
            },
        )
        self.db.execute(
            text("""
                INSERT INTO domain_inventory.silo_lot_movements
                    (id, silo_lot_id, movement_type, quantity_tons, note, tenant_id)
                VALUES (:id, :lot_id, :movement_type, 0, :note, :tenant_id)
            """),
            {
                "id": str(uuid4()),
                "lot_id": lot_d["id"],
                "movement_type": f"qs_{target}",
                "note": reason.strip(),
                "tenant_id": self.tenant_id,
            },
        )
        cell_rows = self.db.execute(
            text("""
                UPDATE domain_inventory.silo_cells
                SET qs_status = :qs_status,
                    updated_at = now()
                WHERE current_lot_id = :lot_id
                  AND tenant_id = :tenant_id
                  AND is_active = true
                RETURNING id, warehouse_id, cell_code
            """),
            {
                "qs_status": target,
                "lot_id": str(lot_d["id"]),
                "tenant_id": self.tenant_id,
            },
        ).mappings().all()

        qty_kg = Decimal(str(lot_d.get("quantity_tons") or "0")) * Decimal("1000")
        payload = {
            "lot_id": str(lot_d["id"]),
            "virtual_lot_number": lot_d.get("virtual_lot_number"),
            "article_id": lot_d.get("article_id"),
            "quantity_kg": float(qty_kg),
            "qs_status": target,
            "lot_status_from": previous_status,
            "lot_status_to": target_lot_status,
            "reason": reason.strip(),
            "operator": operator.strip(),
            "sample_id": sample_id,
            "analysis_id": analysis_id,
            "lab_document_id": lab_document_id,
            "gmp_evidence_id": gmp_evidence_id,
            "vlog_evidence_id": vlog_evidence_id,
            "production_release_ref": production_release_ref,
            "linked_cells": [dict(row) for row in cell_rows],
        }
        event = SupplyChainEventService(self.db, self.tenant_id).record(
            ticket_id=str(lot_d["source_ticket_id"]) if lot_d.get("source_ticket_id") else None,
            stage="lager",
            event_type="qs_status_changed",
            ref_type="silo_lot",
            ref_id=str(lot_d["id"]),
            ref_label=str(lot_d.get("virtual_lot_number") or lot_d["id"]),
            status_from=previous_status,
            status_to=target_lot_status,
            menge_kg=float(qty_kg) if qty_kg else None,
            abweichung_grund=reason.strip(),
            payload=payload,
            bediener=operator.strip(),
            source="manual",
            commit=False,
        )
        self.db.commit()
        return {
            "ok": True,
            "lot_id": str(lot_d["id"]),
            "virtual_lot_number": lot_d.get("virtual_lot_number"),
            "qs_status": target,
            "lot_status": target_lot_status,
            "previous_lot_status": previous_status,
            "linked_cell_count": len(payload["linked_cells"]),
            "linked_cells": payload["linked_cells"],
            "event": event,
        }
