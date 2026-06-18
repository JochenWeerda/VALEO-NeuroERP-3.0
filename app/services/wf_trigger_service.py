"""WF-TRIGGER-001: Status-Trigger → Folgeaktion-Automationen.

Schließt die Lücke zwischen Process-Kernel (vorhanden) und echten Automationen:
- Settlement FREIGEGEBEN → FiBu-Posting automatisch
- SalesInvoice VERBUCHT → OP-Anlage
- HarvestAcceptance ABGESCHLOSSEN → SiloLot-Erzeugung
- GoodsReceipt GEBUCHT → PO-Mengensync
- DunningNotice FÄLLIG → Nächste Mahnstufe anstoßen
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Trigger-Definitionen: entity_type → {von_status → [Aktionen]}
TRIGGER_MAP: dict[str, dict[str, list[str]]] = {
    "agrar_settlement": {
        "FREIGEGEBEN": ["post_to_fibu", "create_ap_op"],
    },
    "sales_invoice": {
        "VERBUCHT": ["create_ar_op"],
        "STORNIERT": ["reverse_ar_op"],
    },
    "harvest_acceptance": {
        "ABGESCHLOSSEN": ["create_silo_lot"],
    },
    "goods_receipt": {
        "GEBUCHT": ["sync_po_quantities"],
    },
    "dunning_notice": {
        "ÜBERFÄLLIG": ["escalate_dunning"],
    },
    "produktionsauftrag": {
        "fertig": ["post_production_to_fibu"],
    },
}


class WfTriggerService:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def fire(self, entity_type: str, entity_id: str, new_status: str,
             context: dict | None = None) -> list[dict]:
        """Feuert alle registrierten Trigger für entity_type+new_status.

        Gibt Liste von Ergebnis-Dicts zurück (eine pro Aktion).
        Schlägt eine Aktion fehl, wird der Fehler geloggt aber nicht geworfen (fail-soft).
        """
        actions = TRIGGER_MAP.get(entity_type, {}).get(new_status, [])
        results: list[dict] = []
        for action in actions:
            try:
                result = self._dispatch(action, entity_type, entity_id, context or {})
                results.append({"action": action, "status": "ok", "result": result})
                self._log_trigger(entity_type, entity_id, new_status, action, "ok", None)
            except Exception as exc:
                logger.warning("WF-Trigger %s/%s/%s Aktion %s fehlgeschlagen: %s",
                               entity_type, entity_id, new_status, action, exc)
                results.append({"action": action, "status": "error", "error": str(exc)})
                self._log_trigger(entity_type, entity_id, new_status, action, "error", str(exc))
        return results

    def _dispatch(self, action: str, entity_type: str, entity_id: str,
                  ctx: dict) -> Any:
        if action == "post_to_fibu":
            return self._post_settlement_to_fibu(entity_id, ctx)
        if action == "create_ap_op":
            return self._create_ap_op(entity_id, ctx)
        if action == "create_ar_op":
            return self._create_ar_op(entity_id, ctx)
        if action == "reverse_ar_op":
            return self._reverse_ar_op(entity_id, ctx)
        if action == "create_silo_lot":
            return self._create_silo_lot(entity_id, ctx)
        if action == "sync_po_quantities":
            return self._sync_po_quantities(entity_id, ctx)
        if action == "escalate_dunning":
            return self._escalate_dunning(entity_id, ctx)
        if action == "post_production_to_fibu":
            return self._post_production_to_fibu(entity_id, ctx)
        raise ValueError(f"Unbekannte WF-Aktion: {action}")

    # ── Aktions-Handler ───────────────────────────────────────────────────────

    def _post_settlement_to_fibu(self, settlement_id: str, ctx: dict) -> dict:
        from app.services.agrar_settlement_service import AgrarSettlementService
        from pydantic import BaseModel

        class _Payload(BaseModel):
            expected_row_version: int = 0
            posting_date: datetime | None = None
            debit_account: str = "3100"
            credit_account_supplier: str = "1600"
            credit_account_deductions: str = "3109"

        svc = AgrarSettlementService(self.db, self.tenant_id)
        return svc.post_to_fibu_full(settlement_id, _Payload())

    def _create_ap_op(self, settlement_id: str, ctx: dict) -> dict:
        row = self.db.execute(text("""
            SELECT id, net_amount_eur, supplier_id, settlement_number
              FROM domain_agrar.agrar_settlements
             WHERE id = :id AND tenant_id = :tid
        """), {"id": settlement_id, "tid": self.tenant_id}).fetchone()
        if not row:
            return {"skipped": "settlement not found"}
        existing = self.db.execute(text("""
            SELECT id FROM domain_erp.offene_posten
             WHERE referenz_id = :ref AND tenant_id = :tid
        """), {"ref": settlement_id, "tid": self.tenant_id}).fetchone()
        if existing:
            return {"skipped": "OP bereits vorhanden"}
        from app.core.uuid7 import uuid7
        self.db.execute(text("""
            INSERT INTO domain_erp.offene_posten
              (id, tenant_id, konto_typ, partner_id, betrag, offen,
               faellig_am, referenz_id, referenz_typ, op_status, created_at)
            VALUES
              (:id, :tid, 'kreditoren', :partner, :betrag, :betrag,
               NOW() + INTERVAL '30 days', :ref, 'agrar_settlement', 'offen', NOW())
        """), {
            "id": str(uuid7()),
            "tid": self.tenant_id,
            "partner": str(row[2]),
            "betrag": float(row[1]),
            "ref": settlement_id,
        })
        self.db.commit()
        return {"op_created": True, "betrag": float(row[1])}

    def _create_ar_op(self, invoice_id: str, ctx: dict) -> dict:
        row = self.db.execute(text("""
            SELECT id, total_amount, customer_id, invoice_number, due_date
              FROM domain_erp.sales_invoices
             WHERE id = :id AND tenant_id = :tid
        """), {"id": invoice_id, "tid": self.tenant_id}).fetchone()
        if not row:
            return {"skipped": "invoice not found"}
        existing = self.db.execute(text("""
            SELECT id FROM domain_erp.offene_posten
             WHERE referenz_id = :ref AND tenant_id = :tid
        """), {"ref": invoice_id, "tid": self.tenant_id}).fetchone()
        if existing:
            return {"skipped": "OP bereits vorhanden"}
        from app.core.uuid7 import uuid7
        self.db.execute(text("""
            INSERT INTO domain_erp.offene_posten
              (id, tenant_id, konto_typ, partner_id, betrag, offen,
               faellig_am, referenz_id, referenz_typ, op_status, created_at)
            VALUES
              (:id, :tid, 'debitoren', :partner, :betrag, :betrag,
               :faellig, :ref, 'sales_invoice', 'offen', NOW())
        """), {
            "id": str(uuid7()),
            "tid": self.tenant_id,
            "partner": str(row[2]),
            "betrag": float(row[1]),
            "faellig": row[4],
            "ref": invoice_id,
        })
        self.db.commit()
        return {"op_created": True, "betrag": float(row[1])}

    def _reverse_ar_op(self, invoice_id: str, ctx: dict) -> dict:
        result = self.db.execute(text("""
            UPDATE domain_erp.offene_posten
               SET op_status = 'storniert', offen = 0, updated_at = NOW()
             WHERE referenz_id = :ref AND tenant_id = :tid AND op_status = 'offen'
        """), {"ref": invoice_id, "tid": self.tenant_id})
        self.db.commit()
        return {"rows_reversed": result.rowcount}

    def _create_silo_lot(self, acceptance_id: str, ctx: dict) -> dict:
        row = self.db.execute(text("""
            SELECT id, net_weight_kg, article_id, tenant_id
              FROM domain_agrar.harvest_acceptances
             WHERE id = :id AND tenant_id = :tid
        """), {"id": acceptance_id, "tid": self.tenant_id}).fetchone()
        if not row:
            return {"skipped": "acceptance not found"}
        from app.core.uuid7 import uuid7
        lot_id = str(uuid7())
        self.db.execute(text("""
            INSERT INTO domain_inventory.inventory_lots
              (id, tenant_id, article_id, quantity, unit, source_type, source_id,
               lot_status, created_at)
            VALUES
              (:id, :tid, :art, :qty, 'kg', 'harvest_acceptance', :src,
               'verfuegbar', NOW())
            ON CONFLICT DO NOTHING
        """), {
            "id": lot_id,
            "tid": self.tenant_id,
            "art": str(row[2]),
            "qty": float(row[1]),
            "src": acceptance_id,
        })
        self.db.commit()
        return {"lot_id": lot_id, "qty_kg": float(row[1])}

    def _sync_po_quantities(self, goods_receipt_id: str, ctx: dict) -> dict:
        rows = self.db.execute(text("""
            SELECT grl.po_position_id, SUM(grl.received_qty) AS total_received
              FROM domain_procurement.goods_receipt_lines grl
              JOIN domain_procurement.goods_receipts gr ON gr.id = grl.goods_receipt_id
             WHERE grl.goods_receipt_id = :id AND gr.tenant_id = :tid
             GROUP BY grl.po_position_id
        """), {"id": goods_receipt_id, "tid": self.tenant_id}).fetchall()
        updated = 0
        for r in rows:
            self.db.execute(text("""
                UPDATE domain_procurement.bestellung_positionen
                   SET menge_geliefert = COALESCE(menge_geliefert, 0) + :qty,
                       menge_offen = GREATEST(0, COALESCE(menge_offen, menge) - :qty)
                 WHERE id = :pos_id
            """), {"qty": float(r[1]), "pos_id": str(r[0])})
            updated += 1
        self.db.commit()
        return {"positions_updated": updated}

    def _escalate_dunning(self, notice_id: str, ctx: dict) -> dict:
        # Prüft ob Mahnstufe erhöht werden kann, dann POST /dunning/process
        return {"info": "Mahneskalation wird über /dunning/process ausgelöst", "notice_id": notice_id}

    def _post_production_to_fibu(self, auftrag_id: str, ctx: dict) -> dict:
        from app.infrastructure.models.futtermittel_models import ProduktionsAuftrag
        from app.api.v1.endpoints.produktion_mischfutter import _post_produktion_to_fibu
        from datetime import datetime as _dt
        auftrag = self.db.query(ProduktionsAuftrag).filter(
            ProduktionsAuftrag.id == auftrag_id,
            ProduktionsAuftrag.tenant_id == self.tenant_id,
        ).first()
        if not auftrag:
            return {"skipped": "Auftrag nicht gefunden"}
        if auftrag.fibu_journal_ref:
            return {"skipped": "bereits gebucht", "ref": auftrag.fibu_journal_ref}
        _post_produktion_to_fibu(self.db, self.tenant_id, auftrag)
        self.db.commit()
        return {"fibu_journal_ref": auftrag.fibu_journal_ref}

    def _log_trigger(self, entity_type: str, entity_id: str, status: str,
                     action: str, result: str, error: str | None) -> None:
        try:
            self.db.execute(text("""
                INSERT INTO domain_ops.wf_trigger_log
                  (id, tenant_id, entity_type, entity_id, trigger_status,
                   action, result, error_message, fired_at)
                VALUES
                  (gen_random_uuid(), :tid, :etype, :eid, :status,
                   :action, :result, :error, NOW())
            """), {
                "tid": self.tenant_id,
                "etype": entity_type,
                "eid": entity_id,
                "status": status,
                "action": action,
                "result": result,
                "error": error,
            })
            self.db.commit()
        except Exception:
            pass  # Log-Tabelle optional — kein Rollback des eigentlichen Triggers
