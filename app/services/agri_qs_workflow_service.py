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
_LOT_STATUS_ATTENTION = frozenset({"in_pruefung", "gesperrt", "reserviert", "reinigung"})
_CELL_QS_ATTENTION = frozenset({"in_pruefung", "gesperrt", "reserviert", "reinigung"})
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

    def list_worklist(self, *, limit: int = 100) -> dict[str, Any]:
        """Lots und Silozellen mit handlungsbeduerftigem QS-Status."""
        safe_limit = max(1, min(limit, 500))
        lot_rows = self.db.execute(
            text("""
                SELECT sl.id, sl.virtual_lot_number, sl.article_id, sl.quantity_tons,
                       sl.status, sl.source_ticket_id, sl.updated_at,
                       COUNT(sc.id) FILTER (WHERE sc.is_active = true) AS linked_cell_count
                FROM domain_inventory.silo_lots sl
                LEFT JOIN domain_inventory.silo_cells sc
                  ON sc.current_lot_id = sl.id::text
                 AND sc.tenant_id = sl.tenant_id
                WHERE sl.tenant_id = :tenant_id
                  AND sl.status = ANY(:attention_statuses)
                GROUP BY sl.id, sl.virtual_lot_number, sl.article_id, sl.quantity_tons,
                         sl.status, sl.source_ticket_id, sl.updated_at
                ORDER BY sl.updated_at DESC NULLS LAST
                LIMIT :limit
            """),
            {
                "tenant_id": self.tenant_id,
                "attention_statuses": list(_LOT_STATUS_ATTENTION),
                "limit": safe_limit,
            },
        ).mappings().all()
        cell_rows = self.db.execute(
            text("""
                SELECT sc.id, sc.cell_code, sc.name, sc.warehouse_id, sc.qs_status,
                       sc.current_lot_id, sc.current_material_id, sc.current_stock_kg,
                       sc.updated_at, sl.virtual_lot_number
                FROM domain_inventory.silo_cells sc
                LEFT JOIN domain_inventory.silo_lots sl
                  ON sl.id::text = sc.current_lot_id
                 AND sl.tenant_id = sc.tenant_id
                WHERE sc.tenant_id = :tenant_id
                  AND sc.is_active = true
                  AND sc.qs_status = ANY(:attention_qs)
                ORDER BY sc.updated_at DESC NULLS LAST
                LIMIT :limit
            """),
            {
                "tenant_id": self.tenant_id,
                "attention_qs": list(_CELL_QS_ATTENTION),
                "limit": safe_limit,
            },
        ).mappings().all()
        lots = []
        for row in lot_rows:
            item = dict(row)
            qty = Decimal(str(item.get("quantity_tons") or "0"))
            item["quantity_kg"] = float(qty * Decimal("1000"))
            item["kind"] = "lot"
            item["qs_status"] = str(item.get("status") or "")
            lots.append(item)
        cells = []
        for row in cell_rows:
            item = dict(row)
            item["kind"] = "cell"
            cells.append(item)
        return {
            "lots": lots,
            "cells": cells,
            "summary": {
                "lot_count": len(lots),
                "cell_count": len(cells),
                "blocked_cells": sum(1 for c in cells if c.get("qs_status") == "gesperrt"),
                "in_review": sum(
                    1 for x in [*lots, *cells]
                    if str(x.get("qs_status") or x.get("status") or "") == "in_pruefung"
                ),
            },
        }

    def suggest_release(self, lot_id: str) -> dict[str, Any]:
        """Deterministischer Freigabe-Vorschlag inkl. Produktionsfreigabe-Regeln."""
        lot = self.db.execute(
            text("""
                SELECT id, virtual_lot_number, source_ticket_id, article_id,
                       quantity_tons, status, moisture_pct, impurities_pct, protein_pct
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
        current_status = str(lot_d.get("status") or "")
        blockers: list[str] = []
        if current_status == "active":
            blockers.append("Lot ist bereits freigegeben (active).")
        if current_status not in {"in_pruefung", "gesperrt", "reserviert", "reinigung"}:
            blockers.append(f"Lot-Status '{current_status}' erlaubt keine QS-Freigabe.")

        sample_id = str(lot_d["source_ticket_id"]) if lot_d.get("source_ticket_id") else None
        analysis_id = f"lot-{lot_d['id']}-inline-qs"
        lab_document_id = None
        has_inline_lab = any(
            lot_d.get(k) is not None for k in ("moisture_pct", "impurities_pct", "protein_pct")
        )
        if not sample_id and not has_inline_lab:
            blockers.append("Kein Wiegeschein und keine Inline-Laborwerte am Lot.")
        elif not sample_id and has_inline_lab:
            sample_id = analysis_id

        blocked_cells = self.db.execute(
            text("""
                SELECT cell_code, qs_status
                FROM domain_inventory.silo_cells
                WHERE current_lot_id = :lot_id
                  AND tenant_id = :tenant_id
                  AND is_active = true
                  AND qs_status = 'gesperrt'
            """),
            {"lot_id": str(lot_d["id"]), "tenant_id": self.tenant_id},
        ).mappings().all()
        if blocked_cells:
            codes = ", ".join(str(r["cell_code"]) for r in blocked_cells)
            blockers.append(f"Verknuepfte Zellen gesperrt: {codes}")

        production_release_allowed = not blockers and bool(sample_id or analysis_id or lab_document_id)
        return {
            "ok": True,
            "lot_id": str(lot_d["id"]),
            "virtual_lot_number": lot_d.get("virtual_lot_number"),
            "current_lot_status": current_status,
            "target_qs_status": "frei",
            "production_release_allowed": production_release_allowed,
            "blockers": blockers,
            "suggested": {
                "sampleId": sample_id,
                "analysisId": analysis_id if has_inline_lab or sample_id else None,
                "labDocumentId": lab_document_id,
                "productionReleaseRef": (
                    f"PROD-RELEASE-{lot_d.get('virtual_lot_number') or lot_d['id']}"
                    if production_release_allowed
                    else None
                ),
                "reason": (
                    "Laborwerte/Wiegeschein vorhanden — Freigabe gemaess QS-Regelwerk"
                    if production_release_allowed
                    else "Manuelle Freigabe mit Laborbezug erforderlich"
                ),
            },
        }
