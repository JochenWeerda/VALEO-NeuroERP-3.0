"""Service layer for compat einkauf domain routes."""
from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import AuditLog
from app.services.finance_transaction_service import FinanceTransactionService
from app.services.compat_helpers import (
    cache_key,
    enqueue_event,
    list_docs,
    now_iso,
    doc_repo,
    safe_float,
)

logger = logging.getLogger(__name__)

_RECHNUNG_TRANSITIONS = {
    "ENTWURF": "GEPRUEFT",
    "ERFASST": "GEPRUEFT",
    "OFFEN": "GEPRUEFT",
    "GEPRUEFT": "FREIGEGEBEN",
    "FREIGEGEBEN": "VERBUCHT",
}


class EinkaufCompatService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def _invalidate(self) -> None:
        try:
            from app.core.cache import cache_delete_prefix
            cache_delete_prefix(cache_key("procurement", self.tenant_id))
        except Exception:
            pass

    # ── Lieferanten ──────────────────────────────────────────────────────────

    def list_suppliers(
        self,
        *,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> dict:
        from sqlalchemy import text
        q = "SELECT * FROM einkauf_lieferanten WHERE tenant_id = :tid"
        params: dict[str, Any] = {"tid": self.tenant_id}
        if search:
            q += " AND (name ILIKE :s OR lieferanten_nummer ILIKE :s)"
            params["s"] = f"%{search}%"
        if is_active is not None:
            q += " AND is_active = :active"
            params["active"] = is_active
        q += " ORDER BY name LIMIT :lim OFFSET :skip"
        params["lim"] = limit
        params["skip"] = skip
        rows = self.db.execute(text(q), params).fetchall()
        return {"items": [dict(r._mapping) for r in rows], "total": len(rows)}

    # ── Field mapping helpers ─────────────────────────────────────────────────

    @staticmethod
    def _anfrage_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "anfrageNummer": m.get("anfrage_nummer") or str(m.get("id")),
            "typ": m.get("typ") or "",
            "anforderer": m.get("anforderer") or "",
            "artikel": m.get("artikel") or "",
            "menge": float(m.get("menge") or 0),
            "prioritaet": m.get("prioritaet") or "normal",
            "status": m.get("status") or "offen",
            "faelligkeit": m.get("datum").isoformat()[:10] if m.get("datum") else None,
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @staticmethod
    def _angebot_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "angebotNummer": m.get("angebots_nummer") or str(m.get("id")),
            "anfrage": str(m.get("anfrage_id") or ""),
            "lieferant": m.get("lieferant_name") or "",
            "artikel": m.get("artikel_name") or "",
            "preis": float(m.get("netto_summe") or 0),
            "gueltigBis": m.get("gueltig_bis").isoformat()[:10] if m.get("gueltig_bis") else None,
            "status": m.get("status") or "offen",
            "lieferzeit": str(m.get("lieferzeit_tage") or ""),
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @staticmethod
    def _anlieferavis_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "avisNummer": m.get("avis_nummer") or str(m.get("id")),
            "bestellung": str(m.get("bestellung_id") or ""),
            "lieferant": m.get("lieferant_name") or "",
            "status": m.get("status") or "offen",
            "geplantesAnlieferDatum": m.get("geplantes_anliefer_datum").isoformat()[:10]
                if m.get("geplantes_anliefer_datum") else None,
            "kennzeichen": m.get("kennzeichen") or "",
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @staticmethod
    def _auftragsbestaetigung_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "bestaetigungsNummer": m.get("bestaetigungs_nummer") or str(m.get("id")),
            "bestellung": str(m.get("bestellung_id") or ""),
            "lieferant": m.get("lieferant_name") or "",
            "status": m.get("status") or "offen",
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    @staticmethod
    def _rechnung_row_to_dict(m: Any) -> dict:
        return {
            "id": str(m.get("id")),
            "rechnungsNummer": m.get("rechnungs_nummer") or str(m.get("id")),
            "lieferant": m.get("lieferant_name") or "",
            "bestellung": str(m.get("bestellung_id") or ""),
            "wareneingang": str(m.get("wareneingang_id") or ""),
            "status": m.get("status") or "OFFEN",
            "bruttoBetrag": float(m.get("brutto_betrag") or 0),
            "rechnungsDatum": m.get("rechnungs_datum").isoformat()[:10]
                if m.get("rechnungs_datum") else None,
            "createdAt": m.get("created_at").isoformat() if m.get("created_at") else None,
        }

    # ── Goods Receipts ────────────────────────────────────────────────────────

    def list_goods_receipts(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                """
                SELECT we.id, we.delivery_note_number AS nummer, we.received_date AS datum,
                       we.quality_inspection_status AS status,
                       COALESCE(po.subject, '') AS lieferant,
                       COALESCE(SUM(pos.accepted_quantity * 0), 0) AS betrag
                FROM einkauf_wareneingaenge we
                LEFT JOIN einkauf_wareneingang_positionen pos ON pos.wareneingang_id = we.id
                LEFT JOIN LATERAL (
                    SELECT data::jsonb->>'subject' AS subject
                    FROM docs_store
                    WHERE doc_type = 'purchase_order'
                      AND (data::jsonb->>'id' = we.purchase_order_id
                           OR data::jsonb->>'purchaseOrderNumber' = we.purchase_order_id)
                    ORDER BY updated_at DESC LIMIT 1
                ) po ON TRUE
                GROUP BY we.id, we.delivery_note_number, we.received_date,
                         we.quality_inspection_status, po.subject
                ORDER BY we.created_at DESC LIMIT 500
                """
            )).fetchall()
        except Exception:
            try:
                rows = self.db.execute(text(
                    "SELECT id, wareneingangs_nummer AS nummer, bestelldatum AS datum, "
                    "status, lieferant_name AS lieferant, brutto_gesamt AS betrag "
                    "FROM einkauf_wareneingaenge ORDER BY created_at DESC LIMIT 500"
                )).fetchall()
            except Exception:
                return []
        return [
            {
                "id": str(r._mapping.get("id")),
                "nummer": r._mapping.get("nummer") or str(r._mapping.get("id")),
                "datum": r._mapping.get("datum").isoformat()[:10] if r._mapping.get("datum") else None,
                "status": r._mapping.get("status") or "offen",
                "lieferant": r._mapping.get("lieferant") or "",
                "betrag": float(r._mapping.get("betrag") or 0),
            }
            for r in rows
        ]

    async def create_goods_receipt(self, payload: dict) -> dict:
        from sqlalchemy import text
        from uuid import uuid4
        receipt_id = str(uuid4())
        purchase_order_id = str(payload.get("purchaseOrderId") or payload.get("purchase_order_id") or "")
        if not purchase_order_id:
            from app.core.exceptions import ValidationFailedError as _VFE
            raise _VFE("purchaseOrderId is required")
        items = payload.get("items") or []
        received_by = str(payload.get("receivedBy") or payload.get("received_by") or "").strip()
        received_location = str(payload.get("receivedLocation") or payload.get("received_location") or "").strip()
        if not received_by or not received_location:
            from app.core.exceptions import ValidationFailedError as _VFE
            raise _VFE("receivedBy and receivedLocation are required")
        received_date = str(payload.get("receivedDate") or payload.get("received_date") or now_iso()[:10])
        delivery_note_number = payload.get("deliveryNoteNumber") or payload.get("delivery_note_number")
        quality_status = str(payload.get("qualityInspectionStatus") or payload.get("quality_inspection_status") or "PENDING")
        inspection_notes = payload.get("inspectionNotes") or payload.get("inspection_notes")
        damage_report = payload.get("damageReport") or payload.get("damage_report")
        self.db.execute(text(
            "INSERT INTO einkauf_wareneingaenge "
            "(id, purchase_order_id, delivery_note_number, received_date, received_by, "
            "received_location, quality_inspection_status, inspection_notes, damage_report, created_at, updated_at) "
            "VALUES (:id, :po_id, :dn, :rd, :rb, :rl, :qs, :ins, :dmg, now(), now())"
        ), {
            "id": receipt_id, "po_id": purchase_order_id, "dn": delivery_note_number,
            "rd": received_date, "rb": received_by, "rl": received_location,
            "qs": quality_status, "ins": inspection_notes, "dmg": damage_report,
        })
        for line in items:
            pos_id = str(uuid4())
            recv_qty = float(line.get("receivedQuantity") or line.get("received_quantity") or 0)
            acc_qty = float(line.get("acceptedQuantity") or line.get("accepted_quantity") or recv_qty)
            rej_qty = float(line.get("rejectedQuantity") or line.get("rejected_quantity") or 0)
            ord_qty = float(line.get("orderedQuantity") or line.get("ordered_quantity") or recv_qty)
            self.db.execute(text(
                "INSERT INTO einkauf_wareneingang_positionen "
                "(id, wareneingang_id, purchase_order_item_id, article_id, article_name, "
                "ordered_quantity, received_quantity, accepted_quantity, rejected_quantity, condition, created_at, updated_at) "
                "VALUES (:id, :wid, :poi, :aid, :an, :oq, :rq, :aq, :jq, :cond, now(), now())"
            ), {
                "id": pos_id, "wid": receipt_id,
                "poi": line.get("purchaseOrderItemId") or line.get("purchase_order_item_id"),
                "aid": line.get("articleId") or line.get("article_id") or "",
                "an": line.get("articleName") or line.get("article_name"),
                "oq": ord_qty, "rq": recv_qty, "aq": acc_qty, "jq": rej_qty,
                "cond": line.get("condition") or "PERFECT",
            })
        await enqueue_event(self.db, event_type="goods_receipt.created",
                            aggregate_id=receipt_id,
                            payload={"receiptId": receipt_id, "purchaseOrderId": purchase_order_id,
                                     "status": quality_status, "receivedDate": received_date,
                                     "itemCount": len(items)},
                            tenant_id=self.tenant_id)
        self._book_wareneingang(receipt_id, received_date, items)
        self._invalidate()
        return {
            "id": receipt_id,
            "purchaseOrderId": purchase_order_id,
            "status": quality_status,
            "message": "Wareneingang erfasst",
        }

    def _book_wareneingang(self, receipt_id: str, received_date: str, items: list) -> None:
        """Book inventory increase on goods receipt: Debit 2000 Warenbestand / Credit 1600 Verbindlichkeiten."""
        from decimal import Decimal
        total_cost = Decimal("0.00")
        for line in items:
            qty = Decimal(str(line.get("acceptedQuantity") or line.get("accepted_quantity") or
                              line.get("receivedQuantity") or line.get("received_quantity") or 0))
            cost = Decimal(str(line.get("unitCost") or line.get("unit_cost") or
                               line.get("unitPrice") or line.get("unit_price") or 0))
            total_cost += (qty * cost).quantize(Decimal("0.01"))
        if total_cost == Decimal("0.00"):
            return
        try:
            entry_date = received_date[:10] if received_date else None
            fin = FinanceTransactionService(self.db, self.tenant_id)
            fin.create(
                entry_number=f"WE-{receipt_id[:8]}",
                description=f"Wareneingang {receipt_id[:8]}",
                entry_date=entry_date,
                lines=[
                    {"account_id": "2000", "debit_amount": float(total_cost), "credit_amount": 0,
                     "description": "Warenbestand Zugang"},
                    {"account_id": "1600", "debit_amount": 0, "credit_amount": float(total_cost),
                     "description": "Verbindlichkeiten Lieferant"},
                ],
                reference=receipt_id[:8],
                source="goods_receipt",
                document_type="wareneingang",
                period=received_date[:7] if received_date else None,
            )
        except Exception:
            pass  # booking failure must not block receipt creation

    # ── Anfragen ──────────────────────────────────────────────────────────────

    def list_anfragen(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, prioritaet, "
                "status, datum, created_at FROM einkauf_anfragen "
                "WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
            ), {"tid": self.tenant_id}).fetchall()
        except Exception:
            return []
        return [self._anfrage_row_to_dict(r._mapping) for r in rows]

    def get_anfrage(self, anfrage_id: str) -> dict:
        from sqlalchemy import text
        try:
            row = self.db.execute(text(
                "SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, prioritaet, "
                "status, datum, created_at FROM einkauf_anfragen "
                "WHERE (id = :fid OR anfrage_nummer = :fid) ORDER BY created_at DESC LIMIT 1"
            ), {"fid": anfrage_id}).fetchone()
        except Exception:
            row = None
        if row is None:
            raise EntityNotFoundError(f"Anfrage {anfrage_id} not found")
        return self._anfrage_row_to_dict(row._mapping)

    def _load_anfrage_raw_row(self, anfrage_id: str) -> Any:
        from sqlalchemy import text
        try:
            return self.db.execute(text(
                "SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, prioritaet, "
                "status, datum, created_at FROM einkauf_anfragen "
                "WHERE (id = :fid OR anfrage_nummer = :fid) AND tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 1"
            ), {"fid": anfrage_id, "tid": self.tenant_id}).fetchone()
        except Exception:
            return None

    async def convert_anfrage_to_order(self, anfrage_id: str) -> dict:
        from sqlalchemy import text
        from app.services.purchase_order_service import PurchaseOrderService
        row = self._load_anfrage_raw_row(anfrage_id)
        if row is None:
            raise EntityNotFoundError(f"Anfrage {anfrage_id} not found")
        m = row._mapping
        po = await PurchaseOrderService(self.db, self.tenant_id).create_purchase_order({
            "subject": m.get("artikel") or f"Anfrage {m.get('anfrage_nummer')}",
            "description": f"Erzeugt aus Anfrage {m.get('anfrage_nummer') or m.get('id')}",
            "deliveryDate": m.get("datum").isoformat()[:10] if m.get("datum") else None,
            "externalReference": m.get("anfrage_nummer") or str(m.get("id")),
            "items": [{"description": m.get("artikel") or "Bedarfsposition",
                       "quantity": float(m.get("menge") or 0), "unitPrice": 0, "unit": "Stk"}],
        })
        self.db.execute(text(
            "UPDATE einkauf_anfragen SET status = 'BESTELLT', updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"id": m.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": "Anfrage in Bestellung ueberfuehrt",
                "purchaseOrderId": po.get("id"),
                "purchaseOrderNumber": po.get("purchaseOrderNumber"),
                "status": "BESTELLT"}

    def list_bids(self, anfrage_id: str) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, angebots_nummer, lieferant_name, netto_summe, waehrung, status, created_at "
                "FROM einkauf_angebote WHERE anfrage_id = :fid ORDER BY created_at DESC"
            ), {"fid": anfrage_id}).fetchall()
        except Exception:
            return []
        return [
            {
                "id": str(r._mapping.get("id")),
                "nummer": r._mapping.get("angebots_nummer") or str(r._mapping.get("id")),
                "lieferant": r._mapping.get("lieferant_name") or "",
                "preis": float(r._mapping.get("netto_summe") or 0),
                "waehrung": r._mapping.get("waehrung") or "EUR",
                "status": r._mapping.get("status") or "offen",
                "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
            }
            for r in rows
        ]

    # ── Angebote ──────────────────────────────────────────────────────────────

    def list_angebote(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, angebots_nummer, anfrage_id, lieferant_name, artikel_name, "
                "netto_summe, gueltig_bis, status, lieferzeit_tage, created_at "
                "FROM einkauf_angebote WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
            ), {"tid": self.tenant_id}).fetchall()
        except Exception:
            return []
        return [self._angebot_row_to_dict(r._mapping) for r in rows]

    def _load_angebot_raw_row(self, angebot_id: str) -> Any:
        from sqlalchemy import text
        try:
            return self.db.execute(text(
                "SELECT id, angebots_nummer, anfrage_id, lieferant_name, artikel_name, "
                "netto_summe, gueltig_bis, status, lieferzeit_tage, created_at "
                "FROM einkauf_angebote "
                "WHERE (id = :aid OR angebots_nummer = :aid) AND tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 1"
            ), {"aid": angebot_id, "tid": self.tenant_id}).fetchone()
        except Exception:
            return None

    def update_angebot_status(
        self, angebot_id: str, new_status: str, change_type: str
    ) -> dict:
        from sqlalchemy import text
        row = self._load_angebot_raw_row(angebot_id)
        if row is None:
            raise EntityNotFoundError(f"Angebot {angebot_id} not found")
        m = row._mapping
        self.db.execute(text(
            "UPDATE einkauf_angebote SET status = :status, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"status": new_status, "id": m.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": f"Angebot {change_type.lower()}", "status": new_status,
                "id": str(m.get("id")),
                "angebotNummer": m.get("angebots_nummer") or str(m.get("id"))}

    async def convert_angebot_to_order(self, angebot_id: str) -> dict:
        from sqlalchemy import text
        from app.services.purchase_order_service import PurchaseOrderService
        row = self._load_angebot_raw_row(angebot_id)
        if row is None:
            raise EntityNotFoundError(f"Angebot {angebot_id} not found")
        m = row._mapping
        po = await PurchaseOrderService(self.db, self.tenant_id).create_purchase_order({
            "subject": m.get("artikel_name") or f"Angebot {m.get('angebots_nummer')}",
            "description": f"Erzeugt aus Angebot {m.get('angebots_nummer') or m.get('id')} "
                           f"von {m.get('lieferant_name') or 'Lieferant'}",
            "deliveryDate": m.get("gueltig_bis").isoformat()[:10] if m.get("gueltig_bis") else None,
            "externalReference": m.get("angebots_nummer") or str(m.get("id")),
            "items": [{"description": m.get("artikel_name") or "Angebotsposition",
                       "quantity": 1,
                       "unitPrice": float(m.get("netto_summe") or 0),
                       "unit": "Stk"}],
            "notes": f"Lieferant: {m.get('lieferant_name') or 'unbekannt'}",
        })
        self.db.execute(text(
            "UPDATE einkauf_angebote SET status = 'IN_BESTELLUNG', updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"id": m.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": "Angebot in Bestellung ueberfuehrt",
                "purchaseOrderId": po.get("id"),
                "purchaseOrderNumber": po.get("purchaseOrderNumber"),
                "status": "IN_BESTELLUNG"}

    # ── Anlieferavis ──────────────────────────────────────────────────────────

    def list_anlieferavis(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, avis_nummer, bestellung_id, lieferant_name, status, "
                "geplantes_anliefer_datum, kennzeichen, created_at "
                "FROM einkauf_anlieferavis WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
            ), {"tid": self.tenant_id}).fetchall()
        except Exception:
            return []
        return [self._anlieferavis_row_to_dict(r._mapping) for r in rows]

    def transition_anlieferavis(self, avis_id: str, action: str) -> dict:
        from sqlalchemy import text
        status_map = {"send": "GESENDET", "confirm": "BESTAETIGT", "cancel": "STORNIERT"}
        if action not in status_map:
            raise ValidationFailedError(f"Unknown action: {action}")
        try:
            row = self.db.execute(text(
                "SELECT id, avis_nummer FROM einkauf_anlieferavis "
                "WHERE (id = :aid OR avis_nummer = :aid) AND tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 1"
            ), {"aid": avis_id, "tid": self.tenant_id}).fetchone()
        except Exception:
            row = None
        if row is None:
            raise EntityNotFoundError(f"Anlieferavis {avis_id} not found")
        new_status = status_map[action]
        self.db.execute(text(
            "UPDATE einkauf_anlieferavis SET status = :status, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"status": new_status, "id": row._mapping.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": f"Anlieferavis {action}", "status": new_status,
                "id": str(row._mapping.get("id")),
                "avisNummer": row._mapping.get("avis_nummer") or str(row._mapping.get("id"))}

    # ── Auftragsbestaetigungen ────────────────────────────────────────────────

    def list_auftragsbestaetigungen(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, bestaetigungs_nummer, bestellung_id, lieferant_name, status, created_at "
                "FROM einkauf_auftragsbestaetigungen WHERE tenant_id = :tid ORDER BY created_at DESC LIMIT 500"
            ), {"tid": self.tenant_id}).fetchall()
        except Exception:
            return []
        return [self._auftragsbestaetigung_row_to_dict(r._mapping) for r in rows]

    def transition_auftragsbestaetigung(self, bestaetigung_id: str, action: str) -> dict:
        from sqlalchemy import text
        status_map = {"review": "GEPRUEFT", "confirm": "BESTAETIGT"}
        if action not in status_map:
            raise ValidationFailedError(f"Unknown action: {action}")
        try:
            row = self.db.execute(text(
                "SELECT id, bestaetigungs_nummer FROM einkauf_auftragsbestaetigungen "
                "WHERE (id = :bid OR bestaetigungs_nummer = :bid) AND tenant_id = :tid "
                "ORDER BY created_at DESC LIMIT 1"
            ), {"bid": bestaetigung_id, "tid": self.tenant_id}).fetchone()
        except Exception:
            row = None
        if row is None:
            raise EntityNotFoundError(f"Auftragsbestaetigung {bestaetigung_id} not found")
        new_status = status_map[action]
        self.db.execute(text(
            "UPDATE einkauf_auftragsbestaetigungen SET status = :status, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = :id AND tenant_id = :tid"
        ), {"status": new_status, "id": row._mapping.get("id"), "tid": self.tenant_id})
        self.db.commit()
        self._invalidate()
        return {"message": f"Auftragsbestaetigung {action}", "status": new_status,
                "id": str(row._mapping.get("id")),
                "bestaetigungsNummer": row._mapping.get("bestaetigungs_nummer") or str(row._mapping.get("id"))}

    # ── Rechnungseingaenge (GoBD) ─────────────────────────────────────────────

    def list_rechnungseingaenge(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, rechnungs_nummer, lieferant_name, bestellung_id, wareneingang_id, "
                "status, brutto_betrag, rechnungs_datum, created_at "
                "FROM einkauf_rechnungseingaenge ORDER BY created_at DESC LIMIT 500"
            )).fetchall()
        except Exception:
            return []
        return [self._rechnung_row_to_dict(r._mapping) for r in rows]

    def _get_rechnung_id_status(self, rechnung_id: str) -> Optional[tuple[str, str]]:
        from sqlalchemy import text
        row = self.db.execute(text(
            "SELECT id, status FROM einkauf_rechnungseingaenge "
            "WHERE id = :id OR rechnungs_nummer = :id"
        ), {"id": rechnung_id}).mappings().first()
        if not row:
            return None
        return (str(row["id"]), (row.get("status") or "").upper())

    def _write_rechnung_audit(
        self, rid: str, action: str, old_status: str, new_status: str
    ) -> None:
        from datetime import datetime as _dt
        from app.core.logging import get_correlation_id
        from sqlalchemy import text
        try:
            row = self.db.execute(text(
                "SELECT id, email FROM domain_shared.users "
                "WHERE tenant_id = :tid AND (is_active IS NULL OR is_active = true) LIMIT 1"
            ), {"tid": self.tenant_id}).mappings().first()
            if not row or not row.get("id"):
                return
            user_id, user_email = str(row["id"]), str((row.get("email") or "unknown")[:100])
        except Exception:
            return
        entry = AuditLog(
            id=uuid7(),
            timestamp=_dt.utcnow(),
            user_id=user_id,
            user_email=user_email,
            tenant_id=self.tenant_id,
            action=action,
            entity_type="rechnungseingang",
            entity_id=rid,
            changes={"old": {"status": old_status}, "new": {"status": new_status}},
            ip_address=None,
            user_agent=None,
            correlation_id=get_correlation_id(),
        )
        self.db.add(entry)

    def _transition_rechnung(self, rechnung_id: str, action: str) -> dict:
        from sqlalchemy import text
        allowed = {
            "pruefen": ({"ENTWURF", "ERFASST", "OFFEN"}, "GEPRUEFT",
                        "Prüfen nur möglich bei Status Entwurf/Erfasst/Offen"),
            "freigeben": ({"GEPRUEFT"}, "FREIGEGEBEN",
                          "Freigeben nur möglich bei Status GEPRUEFT"),
            "verbuchen": ({"FREIGEGEBEN"}, "VERBUCHT",
                          "Verbuchen nur möglich bei Status FREIGEGEBEN"),
        }
        valid_statuses, new_status, err_msg = allowed[action]
        pair = self._get_rechnung_id_status(rechnung_id)
        if not pair:
            raise EntityNotFoundError(f"Rechnungseingang {rechnung_id} nicht gefunden")
        rid, old_status = pair
        if old_status not in valid_statuses:
            raise ValidationFailedError(f"{err_msg}. Aktuell: {old_status}")
        self.db.execute(text(
            "UPDATE einkauf_rechnungseingaenge SET status = :ns, updated_at = now() WHERE id = :id"
        ), {"ns": new_status, "id": rid})
        self._write_rechnung_audit(rid, action, old_status, new_status)
        self.db.commit()
        self._invalidate()
        return {"message": f"Rechnungseingang {action}t", "status": new_status}

    def pruefen_rechnung(self, rechnung_id: str) -> dict:
        return self._transition_rechnung(rechnung_id, "pruefen")

    def freigeben_rechnung(self, rechnung_id: str) -> dict:
        return self._transition_rechnung(rechnung_id, "freigeben")

    def verbuchen_rechnung(self, rechnung_id: str) -> dict:
        return self._transition_rechnung(rechnung_id, "verbuchen")

    # ── Supplier Ratings & Reports ────────────────────────────────────────────

    async def get_supplier_ratings(self) -> dict:
        ratings = list_docs(self.db, "supplier_rating", tenant_id=self.tenant_id)
        return {"items": ratings, "total": len(ratings)}

    def upsert_supplier_rating(self, supplier_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        existing = repo.get("supplier_rating", supplier_id)
        doc = {**(existing or {}), **payload,
               "id": supplier_id, "tenantId": self.tenant_id, "updated_at": now_iso()}
        if not existing:
            doc["created_at"] = now_iso()
        repo.save("supplier_rating", supplier_id, doc)
        self._invalidate()
        return doc

    async def get_reports(self) -> dict:
        return {"lieferantenLeistung": [], "bestellvolumen": [], "generated_at": now_iso()}

    async def get_reports_standard(self) -> dict:
        orders = list_docs(self.db, "purchase_order", tenant_id=self.tenant_id)
        total = sum(safe_float(o.get("total_amount")) for o in orders)
        return {"totalOrders": len(orders), "totalAmount": total,
                "currency": "EUR", "generated_at": now_iso()}

    # ── Retouren ──────────────────────────────────────────────────────────────

    def list_retouren(self) -> list:
        from sqlalchemy import text
        try:
            rows = self.db.execute(text(
                "SELECT id, retouren_nummer, grund, status, created_at, lieferant_name "
                "FROM einkauf_retouren ORDER BY created_at DESC LIMIT 500"
            )).fetchall()
        except Exception:
            return []
        return [
            {
                "id": str(r._mapping.get("id")),
                "nummer": r._mapping.get("retouren_nummer") or str(r._mapping.get("id")),
                "grund": r._mapping.get("grund") or "",
                "status": r._mapping.get("status") or "offen",
                "datum": r._mapping.get("created_at").isoformat()[:10] if r._mapping.get("created_at") else None,
                "lieferant": r._mapping.get("lieferant_name") or "",
            }
            for r in rows
        ]

    def get_retoure(self, retour_id: str) -> dict:
        for r in self.list_retouren():
            if str(r.get("id")) == retour_id or str(r.get("nummer")) == retour_id:
                return r
        raise EntityNotFoundError(f"Retoure {retour_id} not found")

    async def create_retoure(self, payload: dict) -> dict:
        from sqlalchemy import text
        from datetime import datetime as _dt
        retour_id = uuid7()
        nummer = payload.get("nummer") or f"RET-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        try:
            self.db.execute(text(
                "INSERT INTO einkauf_retouren (id, retouren_nummer, grund, status, lieferant_name, created_at) "
                "VALUES (:id, :nr, :grund, :status, :lieferant, now())"
            ), {
                "id": retour_id, "nr": nummer,
                "grund": payload.get("returnReason") or payload.get("grund") or "",
                "status": payload.get("status") or "offen",
                "lieferant": payload.get("supplierName") or "",
            })
        except Exception:
            self.db.rollback()
        await enqueue_event(self.db, event_type="procurement.return.created",
                            aggregate_id=str(retour_id),
                            payload={"nummer": nummer,
                                     "returnReason": payload.get("returnReason") or payload.get("grund"),
                                     "goodsReceiptId": payload.get("goodsReceiptId"),
                                     "createdAt": now_iso()},
                            tenant_id=self.tenant_id)
        self._invalidate()
        return {"id": str(retour_id), "nummer": nummer, "message": "Retoure erfasst"}

    def patch_retoure(self, retour_id: str, payload: dict) -> dict:
        from sqlalchemy import text
        try:
            self.db.execute(text(
                "UPDATE einkauf_retouren SET status = :status, grund = COALESCE(:grund, grund), "
                "updated_at = now() WHERE id = :id OR retouren_nummer = :id"
            ), {"id": retour_id, "status": payload.get("status", "offen"), "grund": payload.get("grund")})
            self.db.commit()
        except Exception:
            self.db.rollback()
        self._invalidate()
        return {"id": retour_id, "status": payload.get("status", "offen"), "ok": True}

    # ── Service Entry Sheets ──────────────────────────────────────────────────

    def list_service_entry_sheets(self, status: Optional[str] = None) -> dict:
        all_ses = list_docs(self.db, "service_entry_sheet", tenant_id=self.tenant_id)
        if status:
            all_ses = [s for s in all_ses if s.get("status") == status]
        return {"items": all_ses, "total": len(all_ses)}

    async def create_service_entry_sheet(self, payload: dict) -> dict:
        from datetime import datetime as _dt
        number = payload.get("number") or f"SES-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        qty = safe_float(payload.get("quantity"))
        unit_price = safe_float(payload.get("unitPrice"))
        doc = {
            "id": uuid7(),
            "number": number,
            "supplierId": payload.get("supplierId"),
            "purchaseOrderId": payload.get("purchaseOrderId"),
            "serviceDate": payload.get("serviceDate") or now_iso()[:10],
            "description": payload.get("description") or "",
            "quantity": qty,
            "unitPrice": unit_price,
            "amount": round(qty * unit_price, 2),
            "status": payload.get("status") or "ERFASST",
            "tenantId": self.tenant_id,
            "createdAt": now_iso(),
            **{k: v for k, v in payload.items()
               if k not in ("number", "supplierId", "purchaseOrderId", "serviceDate",
                            "description", "quantity", "unitPrice", "status")},
        }
        repo = doc_repo(self.db)
        repo.save("service_entry_sheet", number, doc)
        await enqueue_event(self.db, event_type="service_entry_sheet.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        self._invalidate()
        return doc

    def _find_ses(self, ses_id: str) -> Optional[dict]:
        all_ses = list_docs(self.db, "service_entry_sheet", tenant_id=self.tenant_id)
        for s in all_ses:
            if str(s.get("id")) == ses_id or str(s.get("number")) == ses_id:
                return s
        return None

    def update_service_entry_sheet(self, ses_id: str, payload: dict) -> dict:
        target = self._find_ses(ses_id)
        if target is None:
            raise EntityNotFoundError(f"Service Entry Sheet {ses_id} not found")
        target.update({k: v for k, v in payload.items() if v is not None})
        target["updatedAt"] = now_iso()
        repo = doc_repo(self.db)
        repo.save("service_entry_sheet", target["number"], target)
        self._invalidate()
        return target

    # ── Credit / Debit Memos ──────────────────────────────────────────────────

    def list_credit_memos(self) -> list:
        return list_docs(self.db, "credit_memo", tenant_id=self.tenant_id)

    def list_debit_memos(self) -> list:
        return list_docs(self.db, "debit_memo", tenant_id=self.tenant_id)

    async def _create_memo(self, memo_type: str, payload: dict) -> dict:
        from datetime import datetime as _dt
        prefix = "CM" if memo_type == "credit" else "DM"
        number = payload.get("number") or f"{prefix}-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        items = payload.get("items") or []
        net = sum(safe_float(i.get("netAmount")) for i in items)
        tax = sum(safe_float(i.get("taxAmount")) for i in items)
        doc = {
            "id": uuid7(),
            "number": number,
            "supplierId": payload.get("supplierId"),
            "supplierName": payload.get("supplierName") or "",
            "invoiceId": payload.get("invoiceId"),
            "memoDate": payload.get("memoDate") or now_iso()[:10],
            "reason": payload.get("reason") or "",
            "notes": payload.get("notes"),
            "items": items,
            "netAmount": round(net, 2),
            "taxAmount": round(tax, 2),
            "grossAmount": round(net + tax, 2),
            "status": "ERFASST",
            "settled": False,
            "settledInvoiceIds": [],
            "tenantId": self.tenant_id,
            "createdAt": now_iso(),
        }
        repo = doc_repo(self.db)
        repo.save(f"{memo_type}_memo", number, doc)
        await enqueue_event(self.db, event_type=f"{memo_type}_memo.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        self._invalidate()
        return doc

    async def create_credit_memo(self, payload: dict) -> dict:
        return await self._create_memo("credit", payload)

    async def create_debit_memo(self, payload: dict) -> dict:
        return await self._create_memo("debit", payload)

    def _find_memo(self, memo_type: str, memo_id: str) -> Optional[dict]:
        all_memos = list_docs(self.db, f"{memo_type}_memo", tenant_id=self.tenant_id)
        for m in all_memos:
            if str(m.get("id")) == memo_id or str(m.get("number")) == memo_id:
                return m
        return None

    async def _settle_memo(self, memo_type: str, memo_id: str, payload: dict) -> dict:
        target = self._find_memo(memo_type, memo_id)
        if target is None:
            raise EntityNotFoundError(f"{memo_type.capitalize()} Memo {memo_id} not found")
        if target.get("status") == "VERRECHNET":
            raise ConflictError("Memo already settled")
        target["settled"] = True
        target["status"] = "VERRECHNET"
        target["settledInvoiceIds"] = payload.get("invoiceIds", [])
        target["settledAt"] = now_iso()
        repo = doc_repo(self.db)
        repo.save(f"{memo_type}_memo", target["number"], target)
        await enqueue_event(self.db, event_type=f"{memo_type}_memo.settled",
                            aggregate_id=target["id"], payload=target, tenant_id=self.tenant_id)
        self._invalidate()
        return target

    async def settle_credit_memo(self, memo_id: str, payload: dict) -> dict:
        return await self._settle_memo("credit", memo_id, payload)

    async def settle_debit_memo(self, memo_id: str, payload: dict) -> dict:
        return await self._settle_memo("debit", memo_id, payload)

    # ── EDI ───────────────────────────────────────────────────────────────────

    def list_edi_messages(self) -> dict:
        msgs = list_docs(self.db, "edi_message", tenant_id=self.tenant_id)
        return {"items": msgs, "total": len(msgs)}

    async def create_edi_message(self, payload: dict) -> dict:
        from datetime import datetime as _dt
        msg_id = uuid7()
        number = payload.get("number") or f"EDI-{_dt.utcnow().strftime('%Y%m%d%H%M%S')}"
        doc = {
            "id": msg_id,
            "number": number,
            "direction": payload.get("direction") or "outbound",
            "partner": payload.get("partner") or "",
            "messageType": payload.get("messageType") or "ORDERS",
            "status": payload.get("status") or "QUEUED",
            "payload": payload.get("payload") or {},
            "tenantId": self.tenant_id,
            "createdAt": now_iso(),
        }
        repo = doc_repo(self.db)
        repo.save("edi_message", number, doc)
        await enqueue_event(self.db, event_type="procurement.edi.message.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        self._invalidate()
        return doc

    async def ack_edi_message(self, msg_id: str) -> dict:
        all_msgs = list_docs(self.db, "edi_message", tenant_id=self.tenant_id)
        target = next((m for m in all_msgs
                       if str(m.get("id")) == msg_id or str(m.get("number")) == msg_id), None)
        if target is None:
            raise EntityNotFoundError(f"EDI message {msg_id} not found")
        target["status"] = "ACKNOWLEDGED"
        target["ackAt"] = now_iso()
        repo = doc_repo(self.db)
        repo.save("edi_message", target["number"], target)
        await enqueue_event(self.db, event_type="procurement.edi.message.ack",
                            aggregate_id=target["id"], payload=target, tenant_id=self.tenant_id)
        self._invalidate()
        return target

    # ── Audit Trail & Supplier Documents ─────────────────────────────────────

    def get_audit_trail(self, doc_type: str, doc_id: str) -> dict:
        from sqlalchemy import text
        rows = self.db.execute(
            text("SELECT * FROM audit_logs WHERE entity_type = :et AND entity_id = :eid "
                 "AND tenant_id = :tid ORDER BY created_at DESC"),
            {"et": doc_type, "eid": doc_id, "tid": self.tenant_id},
        ).fetchall()
        return {"items": [dict(r._mapping) for r in rows]}

    def list_supplier_documents(self, supplier_id: str) -> list:
        all_docs = list_docs(self.db, "supplier_document", tenant_id=self.tenant_id)
        return [d for d in all_docs if d.get("supplier_id") == supplier_id]

    def create_supplier_document(self, supplier_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "supplier_id": supplier_id, "tenantId": self.tenant_id,
               "created_at": now_iso(), **payload}
        repo.save("supplier_document", doc["id"], doc)
        return doc

    def delete_supplier_document(self, supplier_id: str, doc_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("supplier_document", doc_id)
        if doc is None or doc.get("supplier_id") != supplier_id:
            raise EntityNotFoundError(f"Document {doc_id} not found for supplier {supplier_id}")
        repo.delete("supplier_document", doc_id)
        return {"deleted": True, "id": doc_id}
