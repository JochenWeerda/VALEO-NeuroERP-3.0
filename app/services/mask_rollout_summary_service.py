"""Data service for batch mask rollout screen-summary endpoints (Waves 42–51)."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from app.core.mask_rollout_catalog import MaskRolloutSpec, get_rollout_spec
from app.core.mask_screen_summary_common import (
    build_screen_summary_payload,
    build_tab_page,
    format_optional_date,
)
from app.documents.router_helpers import get_from_store, get_repository
from app.infrastructure.models import StockMovement as StockMovementModel


class MaskRolloutSummaryService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def build_summary(self, screen_id: str, entity_id: str) -> dict[str, Any]:
        spec = get_rollout_spec(screen_id)
        if spec is None:
            raise HTTPException(status_code=404, detail=f"Unknown rollout screen {screen_id}")

        loaders = {
            "lager/stock-movement": self._stock_movement_summary,
            "lager/article-stock": self._article_stock_summary,
            "finance/ap-invoice": self._ap_invoice_summary,
            "finance/ar-open-item": self._ar_open_item_summary,
            "einkauf/purchase-order": self._purchase_order_summary,
            "einkauf/supplier": self._supplier_summary,
            "crm/opportunity": self._opportunity_summary,
            "sales/delivery-note": self._delivery_note_summary,
            "agrar/harvest-settlement": self._harvest_settlement_summary,
            "finance/payment-run": self._payment_run_summary,
        }
        loader = loaders.get(spec.screen_id)
        if loader is None:
            raise HTTPException(status_code=404, detail=f"No loader for {screen_id}")
        return loader(spec, entity_id)

    def build_tab_data(
        self,
        screen_id: str,
        entity_id: str,
        tab_key: str,
        *,
        page: int = 1,
        limit: int = 25,
        q: str | None = None,
    ) -> dict[str, Any]:
        spec = get_rollout_spec(screen_id)
        if spec is None:
            raise HTTPException(status_code=404, detail=f"Unknown rollout screen {screen_id}")
        if tab_key not in spec.lazy_tabs:
            return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

        tab_loaders = {
            "lager/stock-movement": self._stock_movement_tabs,
            "lager/article-stock": self._article_stock_tabs,
            "finance/ap-invoice": self._ap_invoice_tabs,
            "finance/ar-open-item": self._ar_open_item_tabs,
            "einkauf/purchase-order": self._purchase_order_tabs,
            "einkauf/supplier": self._supplier_tabs,
            "crm/opportunity": self._opportunity_tabs,
            "sales/delivery-note": self._delivery_note_tabs,
            "agrar/harvest-settlement": self._harvest_settlement_tabs,
            "finance/payment-run": self._payment_run_tabs,
        }
        loader = tab_loaders.get(spec.screen_id)
        if loader is None:
            return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)
        return loader(spec, entity_id, tab_key, page=page, limit=limit, q=q)

    def _stock_movement_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = (
            self.db.query(StockMovementModel)
            .filter(StockMovementModel.tenant_id == self.tenant_id, StockMovementModel.id == entity_id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Stock movement not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=row.movement_number or entity_id,
            subtitle=str(row.movement_type or ""),
            summary={
                "movement_type": str(row.movement_type or ""),
                "quantity": float(row.quantity or 0),
                "unit": str(row.unit or ""),
                "article_id": str(row.article_id),
                "warehouse_id": str(row.warehouse_id),
                "movement_date": format_optional_date(row.movement_date),
                "reference_number": str(row.reference_number or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="movement_id",
            actions=[{"key": "edit", "label": "Bearbeiten", "permission": "inventory.movement.update"}],
        )

    def _stock_movement_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        row = (
            self.db.query(StockMovementModel)
            .filter(StockMovementModel.tenant_id == self.tenant_id, StockMovementModel.id == entity_id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Stock movement not found")
        if tab_key == "details":
            items = [
                {
                    "field": "charge",
                    "value": row.charge or "-",
                },
                {
                    "field": "warehouse_location",
                    "value": row.warehouse_location or "-",
                },
                {
                    "field": "unit_cost",
                    "value": float(row.unit_cost) if row.unit_cost is not None else None,
                },
                {
                    "field": "booking_user",
                    "value": row.booking_user or "-",
                },
                {
                    "field": "notes",
                    "value": row.notes or "-",
                },
            ]
            return build_tab_page(tab_key=tab_key, table_key="movement_details", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _article_stock_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, article_number, name, current_stock, available_stock, reserved_stock, unit
                FROM domain_inventory.articles
                WHERE tenant_id = :tenant_id AND id = :article_id
                """
            ),
            {"tenant_id": self.tenant_id, "article_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Article not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["article_number"] or entity_id),
            subtitle=str(row["name"] or ""),
            summary={
                "current_stock": float(row["current_stock"] or 0),
                "available_stock": float(row["available_stock"] or 0),
                "reserved_stock": float(row["reserved_stock"] or 0),
                "unit": str(row["unit"] or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="article_id",
        )

    def _article_stock_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key == "bestand":
            rows = self.db.execute(
                text(
                    """
                    SELECT bs.id, w.name AS warehouse_name, bs.quantity_kg, bs.reserved_kg
                    FROM domain_inventory.bin_stock bs
                    JOIN domain_inventory.warehouse_bins wb ON wb.id = bs.bin_id
                    JOIN domain_inventory.warehouse_zones wz ON wz.id = wb.zone_id
                    JOIN domain_inventory.warehouses w ON w.id = wz.warehouse_id
                    JOIN domain_inventory.articles a ON a.id = bs.article_id
                    WHERE a.tenant_id = :tenant_id AND a.id = :article_id
                    ORDER BY w.name
                    """
                ),
                {"tenant_id": self.tenant_id, "article_id": entity_id},
            ).mappings().all()
            items = [
                {
                    "warehouse_name": r["warehouse_name"],
                    "quantity_kg": float(r["quantity_kg"] or 0),
                    "reserved_kg": float(r["reserved_kg"] or 0),
                }
                for r in rows
            ]
            return build_tab_page(tab_key=tab_key, table_key="bin_stock", items=items, page=page, limit=limit, q=q)

        if tab_key == "bewegungen":
            rows = (
                self.db.query(StockMovementModel)
                .filter(
                    StockMovementModel.tenant_id == self.tenant_id,
                    StockMovementModel.article_id == entity_id,
                )
                .order_by(desc(StockMovementModel.created_at))
                .limit(200)
                .all()
            )
            items = [
                {
                    "movement_id": str(r.id),
                    "movement_number": r.movement_number,
                    "movement_type": r.movement_type,
                    "quantity": float(r.quantity or 0),
                    "movement_date": format_optional_date(r.movement_date),
                }
                for r in rows
            ]
            return build_tab_page(tab_key=tab_key, table_key="recent_movements", items=items, page=page, limit=limit, q=q)

        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _ap_invoice_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        repo = get_repository(self.db)
        invoice = get_from_store("ap_invoice", entity_id, repo)
        if not invoice:
            raise HTTPException(status_code=404, detail="AP Invoice not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(invoice.get("number") or entity_id),
            subtitle=str(invoice.get("customerId") or ""),
            summary={
                "status": str(invoice.get("semantic_status") or invoice.get("status") or ""),
                "date": str(invoice.get("date") or ""),
                "due_date": str(invoice.get("dueDate") or ""),
                "total_gross": float(invoice.get("totalGross") or 0),
                "line_count": len(invoice.get("lines") or []),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="invoice_id",
            actions=[{"key": "edit", "label": "Bearbeiten", "permission": "finance.ap.update"}],
        )

    def _ap_invoice_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        repo = get_repository(self.db)
        invoice = get_from_store("ap_invoice", entity_id, repo)
        if not invoice:
            raise HTTPException(status_code=404, detail="AP Invoice not found")
        if tab_key == "positionen":
            lines = invoice.get("lines") or []
            items = [
                {
                    "position": idx + 1,
                    "description": line.get("description") or line.get("itemDescription") or "",
                    "quantity": float(line.get("quantity") or 0),
                    "unit_price": float(line.get("unitPrice") or 0),
                    "total": float(line.get("total") or line.get("lineTotal") or 0),
                }
                for idx, line in enumerate(lines)
            ]
            return build_tab_page(tab_key=tab_key, table_key="invoice_lines", items=items, page=page, limit=limit, q=q)
        if tab_key == "freigabe":
            items = [
                {"key": "approval_status", "value": invoice.get("approval_status") or invoice.get("status") or "-"},
                {"key": "semantic_status", "value": invoice.get("semantic_status") or "-"},
            ]
            return build_tab_page(tab_key=tab_key, table_key="approval", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _resolve_op_schema(self) -> str:
        row = self.db.execute(
            text(
                """
                SELECT table_schema
                FROM information_schema.tables
                WHERE table_name = 'offene_posten'
                ORDER BY CASE WHEN table_schema = 'domain_erp' THEN 0 ELSE 1 END
                LIMIT 1
                """
            )
        ).first()
        return row[0] if row else "domain_erp"

    def _ar_open_item_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        schema = self._resolve_op_schema()
        row = self.db.execute(
            text(
                f"""
                SELECT id, beleg_nr, konto_nr, konto_name, konto_typ, offener_betrag, faellig_am, status
                FROM {schema}.offene_posten
                WHERE tenant_id = :tenant_id AND id = :op_id
                """
            ),
            {"tenant_id": self.tenant_id, "op_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Open item not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["beleg_nr"] or entity_id),
            subtitle=str(row["konto_name"] or row["konto_nr"] or ""),
            summary={
                "konto_typ": str(row["konto_typ"] or ""),
                "offener_betrag": float(row["offener_betrag"] or 0),
                "faellig_am": format_optional_date(row["faellig_am"]),
                "status": str(row["status"] or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="op_id",
        )

    def _ar_open_item_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key != "ausgleich":
            return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)
        schema = self._resolve_op_schema()
        rows = self.db.execute(
            text(
                f"""
                SELECT id, betrag, buchungs_datum, referenz, notiz
                FROM {schema}.op_ausgleich
                WHERE tenant_id = :tenant_id AND op_id = :op_id
                ORDER BY buchungs_datum DESC NULLS LAST
                """
            ),
            {"tenant_id": self.tenant_id, "op_id": entity_id},
        ).mappings().all()
        items = [
            {
                "betrag": float(r["betrag"] or 0),
                "buchungs_datum": format_optional_date(r["buchungs_datum"]),
                "referenz": r["referenz"] or "",
                "notiz": r["notiz"] or "",
            }
            for r in rows
        ]
        return build_tab_page(tab_key=tab_key, table_key="settlements", items=items, page=page, limit=limit, q=q)

    def _purchase_order_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, bestell_nr, lieferant_id, status, bestelldatum, gesamtbetrag, waehrung
                FROM domain_einkauf.bestellungen
                WHERE tenant_id = :tenant_id AND id = :bestellung_id
                """
            ),
            {"tenant_id": self.tenant_id, "bestellung_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["bestell_nr"] or entity_id),
            subtitle=str(row["lieferant_id"] or ""),
            summary={
                "status": str(row["status"] or ""),
                "bestelldatum": format_optional_date(row["bestelldatum"]),
                "gesamtbetrag": float(row["gesamtbetrag"] or 0),
                "waehrung": str(row["waehrung"] or "EUR"),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="bestellung_id",
            actions=[{"key": "edit", "label": "Bearbeiten", "permission": "einkauf.bestellung.update"}],
        )

    def _purchase_order_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key == "positionen":
            rows = self.db.execute(
                text(
                    """
                    SELECT position_nr, artikel_nr, bezeichnung, menge, einheit, einzelpreis, gesamtpreis
                    FROM domain_einkauf.bestellung_positionen
                    WHERE tenant_id = :tenant_id AND bestellung_id = :bestellung_id
                    ORDER BY position_nr
                    """
                ),
                {"tenant_id": self.tenant_id, "bestellung_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="po_lines", items=items, page=page, limit=limit, q=q)
        if tab_key == "kommunikation":
            rows = self.db.execute(
                text(
                    """
                    SELECT kanal, empfaenger, versendet_am, status
                    FROM domain_einkauf.bestellung_kommunikation
                    WHERE tenant_id = :tenant_id AND bestellung_id = :bestellung_id
                    ORDER BY versendet_am DESC NULLS LAST
                    """
                ),
                {"tenant_id": self.tenant_id, "bestellung_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="po_comms", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _supplier_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, lieferanten_nr, name, status, email, telefon
                FROM domain_einkauf.lieferanten
                WHERE tenant_id = :tenant_id AND id = :lieferant_id
                """
            ),
            {"tenant_id": self.tenant_id, "lieferant_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["lieferanten_nr"] or entity_id),
            subtitle=str(row["name"] or ""),
            summary={
                "status": str(row["status"] or ""),
                "email": str(row["email"] or ""),
                "telefon": str(row["telefon"] or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="lieferant_id",
        )

    def _supplier_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key == "bestellungen":
            rows = self.db.execute(
                text(
                    """
                    SELECT id, bestell_nr, status, bestelldatum, gesamtbetrag
                    FROM domain_einkauf.bestellungen
                    WHERE tenant_id = :tenant_id AND lieferant_id = :lieferant_id
                    ORDER BY bestelldatum DESC NULLS LAST
                    LIMIT 200
                    """
                ),
                {"tenant_id": self.tenant_id, "lieferant_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="supplier_pos", items=items, page=page, limit=limit, q=q)
        if tab_key == "kontakte":
            rows = self.db.execute(
                text(
                    """
                    SELECT name, rolle, email, telefon
                    FROM domain_einkauf.lieferant_kontakte
                    WHERE tenant_id = :tenant_id AND lieferant_id = :lieferant_id
                    ORDER BY name
                    """
                ),
                {"tenant_id": self.tenant_id, "lieferant_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="supplier_contacts", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _opportunity_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, title, stage, amount, probability, expected_close_date, customer_id
                FROM domain_crm.crm_opportunities
                WHERE tenant_id = :tenant_id AND id = :opportunity_id
                """
            ),
            {"tenant_id": self.tenant_id, "opportunity_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["title"] or entity_id),
            subtitle=str(row["stage"] or ""),
            summary={
                "stage": str(row["stage"] or ""),
                "amount": float(row["amount"] or 0),
                "probability": float(row["probability"] or 0),
                "expected_close_date": format_optional_date(row["expected_close_date"]),
                "customer_id": str(row["customer_id"] or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="opportunity_id",
        )

    def _opportunity_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key == "aktivitaeten":
            rows = self.db.execute(
                text(
                    """
                    SELECT id, activity_type, subject, due_date, status
                    FROM domain_crm.crm_activities
                    WHERE tenant_id = :tenant_id AND opportunity_id = :opportunity_id
                    ORDER BY due_date DESC NULLS LAST
                    LIMIT 200
                    """
                ),
                {"tenant_id": self.tenant_id, "opportunity_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="activities", items=items, page=page, limit=limit, q=q)
        if tab_key == "angebote":
            rows = self.db.execute(
                text(
                    """
                    SELECT id, quote_number, status, total_amount, valid_until
                    FROM domain_crm.crm_quotes
                    WHERE tenant_id = :tenant_id AND opportunity_id = :opportunity_id
                    ORDER BY valid_until DESC NULLS LAST
                    LIMIT 200
                    """
                ),
                {"tenant_id": self.tenant_id, "opportunity_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="quotes", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _delivery_note_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, delivery_number, customer_id, status, delivery_date, order_id
                FROM domain_sales.delivery_notes
                WHERE tenant_id = :tenant_id AND id = :ls_id
                """
            ),
            {"tenant_id": self.tenant_id, "ls_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Delivery note not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["delivery_number"] or entity_id),
            subtitle=str(row["customer_id"] or ""),
            summary={
                "status": str(row["status"] or ""),
                "delivery_date": format_optional_date(row["delivery_date"]),
                "order_id": str(row["order_id"] or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="ls_id",
        )

    def _delivery_note_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key == "positionen":
            rows = self.db.execute(
                text(
                    """
                    SELECT position_no, article_id, description, quantity, unit
                    FROM domain_sales.delivery_note_positions
                    WHERE tenant_id = :tenant_id AND delivery_note_id = :ls_id
                    ORDER BY position_no
                    """
                ),
                {"tenant_id": self.tenant_id, "ls_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="delivery_lines", items=items, page=page, limit=limit, q=q)
        if tab_key == "dokumente":
            items = [{"document_type": "Lieferschein", "reference": entity_id}]
            return build_tab_page(tab_key=tab_key, table_key="documents", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _harvest_settlement_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, settlement_number, status, net_amount, gross_amount, weighing_ticket_id
                FROM domain_inventory.agrar_settlements
                WHERE tenant_id = :tenant_id AND id = :settlement_id
                """
            ),
            {"tenant_id": self.tenant_id, "settlement_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Settlement not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["settlement_number"] or entity_id),
            subtitle=str(row["status"] or ""),
            summary={
                "status": str(row["status"] or ""),
                "net_amount": float(row["net_amount"] or 0),
                "gross_amount": float(row["gross_amount"] or 0),
                "weighing_ticket_id": str(row["weighing_ticket_id"] or ""),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="settlement_id",
        )

    def _harvest_settlement_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key == "abzuege":
            rows = self.db.execute(
                text(
                    """
                    SELECT deduction_type, amount, reason
                    FROM domain_inventory.agrar_settlement_deductions
                    WHERE tenant_id = :tenant_id AND settlement_id = :settlement_id
                    ORDER BY deduction_type
                    """
                ),
                {"tenant_id": self.tenant_id, "settlement_id": entity_id},
            ).mappings().all()
            items = [dict(r) for r in rows]
            return build_tab_page(tab_key=tab_key, table_key="deductions", items=items, page=page, limit=limit, q=q)
        if tab_key == "positionen":
            items = [{"position": 1, "description": "Ernte-Abrechnung", "settlement_id": entity_id}]
            return build_tab_page(tab_key=tab_key, table_key="settlement_lines", items=items, page=page, limit=limit, q=q)
        return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)

    def _payment_run_summary(self, spec: MaskRolloutSpec, entity_id: str) -> dict[str, Any]:
        row = self.db.execute(
            text(
                """
                SELECT id, run_number, execution_date, total_amount, payment_count, status
                FROM domain_erp.payment_runs
                WHERE tenant_id = :tenant_id AND id = :run_id
                """
            ),
            {"tenant_id": self.tenant_id, "run_id": entity_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Payment run not found")
        return build_screen_summary_payload(
            screen_id=spec.screen_id,
            entity_id=entity_id,
            tenant_id=self.tenant_id,
            title=str(row["run_number"] or entity_id),
            subtitle=str(row["status"] or ""),
            summary={
                "status": str(row["status"] or ""),
                "execution_date": format_optional_date(row["execution_date"]),
                "total_amount": float(row["total_amount"] or 0),
                "payment_count": int(row["payment_count"] or 0),
            },
            available_tabs=list(spec.available_tabs),
            api_prefix=spec.api_prefix,
            lazy_tab_keys=list(spec.lazy_tabs),
            initial_payload_budget_kb=spec.budget_kb,
            entity_key="run_id",
            actions=[{"key": "approve", "label": "Freigeben", "permission": "finance.payment_run.approve"}],
        )

    def _payment_run_tabs(
        self,
        spec: MaskRolloutSpec,
        entity_id: str,
        tab_key: str,
        *,
        page: int,
        limit: int,
        q: str | None,
    ) -> dict[str, Any]:
        if tab_key != "zahlungen":
            return build_tab_page(tab_key=tab_key, table_key=tab_key, items=[], page=page, limit=limit, q=q)
        rows = self.db.execute(
            text(
                """
                SELECT creditor_name, iban, amount, purpose, invoice_number, status
                FROM domain_erp.payment_run_items
                WHERE payment_run_id = :run_id
                ORDER BY created_at
                """
            ),
            {"run_id": entity_id},
        ).mappings().all()
        items = [dict(r) for r in rows]
        return build_tab_page(tab_key=tab_key, table_key="payments", items=items, page=page, limit=limit, q=q)
