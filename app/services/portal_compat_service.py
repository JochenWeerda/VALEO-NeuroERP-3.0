"""Service layer for compat portal domain routes (supplier/customer portal)."""
from __future__ import annotations

import logging
import uuid as _uuid_mod
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import Article as ArticleModel
from app.domains.operations.models import Dokument, Rahmenvertrag, ZertifikatEintrag
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class PortalCompatService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Dashboard ─────────────────────────────────────────────────────────────

    def get_dashboard(self) -> dict:
        orders = list_docs(self.db, "portal_order", tenant_id=self.tenant_id)
        contracts = list_docs(self.db, "portal_contract", tenant_id=self.tenant_id)
        return {
            "open_orders": len([o for o in orders if o.get("status") == "OFFEN"]),
            "active_contracts": len([c for c in contracts if c.get("status") == "AKTIV"]),
            "total_orders": len(orders),
            "generated_at": now_iso(),
        }

    # ── Orders ────────────────────────────────────────────────────────────────

    def list_orders(self, status: Optional[str] = None) -> list:
        orders = list_docs(self.db, "portal_order", tenant_id=self.tenant_id)
        if status:
            orders = [o for o in orders if o.get("status") == status]
        return orders

    def get_order(self, order_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError(f"Portal order {order_id} not found")
        return doc

    async def create_order(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("portal_order", doc["id"], doc)
        await enqueue_event(self.db, event_type="portal_order.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def update_order(self, order_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError(f"Portal order {order_id} not found")
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("portal_order", order_id, doc)
        return doc

    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError(f"Portal order {order_id} not found")
        if doc.get("status") in ("STORNIERT", "ABGESCHLOSSEN"):
            from app.core.exceptions import ConflictError
            raise ConflictError("Order cannot be cancelled in current status")
        doc["status"] = "STORNIERT"
        if reason:
            doc["storno_reason"] = reason
        doc["cancelled_at"] = now_iso()
        repo.save("portal_order", order_id, doc)
        await enqueue_event(self.db, event_type="portal_order.cancelled",
                            aggregate_id=order_id, payload=doc, tenant_id=self.tenant_id)
        return doc

    # ── Products ──────────────────────────────────────────────────────────────

    def list_products(self) -> list:
        return list_docs(self.db, "portal_product", tenant_id=self.tenant_id)

    def get_product(self, product_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_product", product_id)
        if doc is None:
            raise EntityNotFoundError(f"Product {product_id} not found")
        return doc

    # ── Contracts ─────────────────────────────────────────────────────────────

    def list_contracts(self) -> list:
        return list_docs(self.db, "portal_contract", tenant_id=self.tenant_id)

    def get_contract(self, contract_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_contract", contract_id)
        if doc is None:
            raise EntityNotFoundError(f"Contract {contract_id} not found")
        return doc

    # ── Invoices ──────────────────────────────────────────────────────────────

    def list_invoices(self) -> list:
        return list_docs(self.db, "portal_invoice", tenant_id=self.tenant_id)

    def get_invoice(self, invoice_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_invoice", invoice_id)
        if doc is None:
            raise EntityNotFoundError(f"Invoice {invoice_id} not found")
        return doc

    # ── Notifications ─────────────────────────────────────────────────────────

    def list_notifications(self) -> list:
        return list_docs(self.db, "portal_notification", tenant_id=self.tenant_id)

    def mark_notification_read(self, notification_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_notification", notification_id)
        if doc is None:
            raise EntityNotFoundError(f"Notification {notification_id} not found")
        doc["read"] = True
        doc["read_at"] = now_iso()
        repo.save("portal_notification", notification_id, doc)
        return doc

    # ── Prices ────────────────────────────────────────────────────────────────

    def list_prices(self) -> list:
        return list_docs(self.db, "portal_price", tenant_id=self.tenant_id)

    # ── Documents ─────────────────────────────────────────────────────────────

    def list_documents(self, doc_type: Optional[str] = None) -> list:
        docs = list_docs(self.db, "portal_document", tenant_id=self.tenant_id)
        if doc_type:
            docs = [d for d in docs if d.get("doc_type") == doc_type]
        return docs

    async def upload_document(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "created_at": now_iso(), **payload}
        repo.save("portal_document", doc["id"], doc)
        return doc

    # ── Full-featured dashboard (with Dokument ORM) ───────────────────────────

    def get_portal_dashboard_full(self) -> dict:
        orders = list_docs(self.db, "sales_order", limit=20)
        invoices = list_docs(self.db, "sales_invoice", limit=20)
        try:
            docs = self.db.query(Dokument).order_by(Dokument.hochgeladen_am.desc()).limit(5).all()
        except Exception:
            docs = []
        offene_rechnungen = sum(1 for i in invoices if str(i.get("status", "")).lower() in {"offen", "ueberfaellig"})
        return {
            "kpis": [
                {"label": "Bestellungen", "value": str(len(orders))},
                {"label": "Rechnungen offen", "value": str(offene_rechnungen)},
                {"label": "Dokumente", "value": str(len(docs))},
            ],
            "letzteBestellungen": [
                {
                    "id": o.get("id") or o.get("number"),
                    "nummer": o.get("number") or o.get("id"),
                    "datum": o.get("date"),
                    "betrag": float(o.get("totalGross") or 0),
                    "status": str(o.get("status") or "offen").lower(),
                }
                for o in orders[:5]
            ],
            "neueDokumente": [
                {
                    "id": d.id,
                    "name": d.name,
                    "datum": d.hochgeladen_am.isoformat()[:10] if d.hochgeladen_am else None,
                    "typ": d.typ,
                }
                for d in docs
            ],
        }

    def list_portal_anfragen(self) -> list:
        docs = list_docs(self.db, "customer_inquiry", limit=500)
        return [
            {
                "id": d.get("id") or d.get("number"),
                "nummer": d.get("number"),
                "betreff": d.get("subject") or d.get("topic") or "Anfrage",
                "datum": d.get("date"),
                "status": str(d.get("status") or "offen").lower(),
            }
            for d in docs
        ]

    def list_portal_bestellungen(self) -> list:
        docs = list_docs(self.db, "sales_order", limit=500)
        return [
            {
                "id": d.get("id") or d.get("number"),
                "nummer": d.get("number"),
                "datum": d.get("date"),
                "artikel": (d.get("lines") or [{}])[0].get("article") if d.get("lines") else "",
                "menge": sum(float(line.get("qty") or 0) for line in (d.get("lines") or [])),
                "betrag": float(d.get("totalGross") or 0),
                "status": str(d.get("status") or "bestellt").lower(),
            }
            for d in docs
        ]

    def list_portal_dokumente(self) -> list:
        try:
            docs = self.db.query(Dokument).order_by(Dokument.hochgeladen_am.desc()).limit(500).all()
        except Exception:
            docs = []
        return [
            {
                "id": d.id,
                "name": d.name,
                "kategorie": d.kategorie,
                "datum": d.hochgeladen_am.isoformat()[:10] if d.hochgeladen_am else None,
                "groesse": int(d.groesse or 0),
                "typ": d.typ,
            }
            for d in docs
        ]

    def list_portal_feldbuch(self, customer_id: Optional[str] = None) -> list:
        from app.infrastructure.models.agrar_models import FeldbuchSchlag
        q = self.db.query(FeldbuchSchlag)
        if self.tenant_id:
            q = q.filter(FeldbuchSchlag.tenant_id == self.tenant_id)
        if customer_id:
            q = q.filter(FeldbuchSchlag.customer_id == customer_id)
        schlaege = q.order_by(FeldbuchSchlag.name).all()
        if schlaege:
            return [
                {"id": s.id, "schlag": s.name, "kultur": s.kultur or "",
                 "flaeche": s.flaeche, "letzteMassnahme": None, "naechsteMassnahme": None}
                for s in schlaege
            ]
        deliveries = list_docs(self.db, "sales_delivery", limit=1000)
        return [
            {
                "id": d.get("number") or d.get("id"),
                "schlag": d.get("fieldName") or "Schlag unbekannt",
                "kultur": d.get("crop") or "",
                "flaeche": float(d.get("areaHa") or 0),
                "letzteMassnahme": d.get("date"),
                "naechsteMassnahme": None,
            }
            for d in deliveries
        ]

    def list_portal_naehrstoffbilanzen(self) -> list:
        deliveries = list_docs(self.db, "sales_delivery", limit=2000)
        return [
            {
                "id": d.get("number") or d.get("id"),
                "schlag": d.get("fieldName") or "Gesamt",
                "kultur": d.get("crop") or "",
                "n_saldo": float(d.get("totalNutrientNKg") or 0),
                "p_saldo": float(d.get("totalNutrientP2o5Kg") or 0),
                "k_saldo": float(d.get("totalNutrientKKg") or 0),
                "bewertung": "ok" if float(d.get("totalNutrientNKg") or 0) <= 170 else "warnung",
            }
            for d in deliveries
        ]

    def list_portal_rechnungen(self) -> list:
        invoices = list_docs(self.db, "sales_invoice", limit=500)
        return [
            {
                "id": i.get("id") or i.get("number"),
                "nummer": i.get("number"),
                "datum": i.get("date"),
                "betrag": float(i.get("totalGross") or 0),
                "status": str(i.get("status") or "offen").lower(),
            }
            for i in invoices
        ]

    def list_portal_shop(self) -> list:
        articles = (
            self.db.query(ArticleModel)
            .filter(ArticleModel.is_active == True)  # noqa: E712
            .order_by(ArticleModel.name.asc())
            .limit(500)
            .all()
        )
        return [
            {
                "id": a.id,
                "name": a.name,
                "kategorie": a.category or "sonstiges",
                "preis": float(a.sales_price or 0),
                "einheit": a.unit,
                "verfuegbar": float(a.available_stock or 0) > 0,
            }
            for a in articles
        ]

    def list_portal_products(
        self,
        kategorie: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> dict:
        q = self.db.query(ArticleModel).filter(ArticleModel.is_active == True)  # noqa: E712
        if kategorie and kategorie != "alle":
            q = q.filter(ArticleModel.category == kategorie)
        if search:
            q = q.filter(ArticleModel.name.ilike(f"%{search}%"))
        total = q.count()
        articles = q.order_by(ArticleModel.name.asc()).offset(skip).limit(limit).all()
        items = [
            {
                "id": str(a.id),
                "artikelnummer": str(getattr(a, "article_number", a.id)),
                "name": a.name,
                "kategorie": a.category or "sonstiges",
                "beschreibung": getattr(a, "description", None) or "",
                "einheit": a.unit or "Stk",
                "preis": float(a.sales_price or 0),
                "rabattPreis": None,
                "verfuegbar": float(a.available_stock or 0) > 0,
                "bestand": float(a.available_stock or 0),
                "zertifikate": [],
                "letzteBestellung": None,
                "contractStatus": "NONE",
                "contractPrice": None,
                "contractRemainingQty": None,
                "contractTotalQty": None,
                "isPrePurchase": False,
                "prePurchasePrice": None,
                "prePurchaseTotalQty": None,
                "prePurchaseRemainingQty": None,
            }
            for a in articles
        ]
        return {"items": items, "total": total, "page": skip // limit if limit else 0, "size": limit,
                "has_contracts": 0, "has_pre_purchases": 0}

    def list_sales_orders(self, skip: int = 0, limit: int = 50, status_filter: Optional[str] = None) -> dict:
        orders = list_docs(self.db, "sales_order", limit=limit, tenant_id=self.tenant_id)
        if status_filter:
            orders = [o for o in orders if o.get("status") == status_filter]
        items = [
            {
                "id": o.get("id", ""),
                "order_number": o.get("number") or o.get("order_number", ""),
                "order_date": (o.get("created_at", "")[:10] if o.get("created_at") else
                               o.get("datum", "")[:10] if o.get("datum") else ""),
                "status": o.get("status", "SUBMITTED"),
                "item_count": len(o.get("positions") or o.get("items") or []),
                "total_net": float(o.get("total_net") or o.get("total_amount") or o.get("totalAmount") or 0),
                "main_article": (
                    (o.get("positions") or o.get("items") or [{}])[0].get("bezeichnung") or
                    (o.get("positions") or o.get("items") or [{}])[0].get("name") or ""
                ) if (o.get("positions") or o.get("items")) else "",
            }
            for o in orders
        ]
        return {"items": items, "total": len(items)}

    def get_sales_order(self, order_id: str) -> dict:
        orders = list_docs(self.db, "sales_order", limit=1000, tenant_id=self.tenant_id)
        for o in orders:
            if str(o.get("id")) == order_id:
                return o
        raise EntityNotFoundError(f"Bestellung {order_id} nicht gefunden")

    def create_sales_order(self, body: dict) -> dict:
        from app.documents.router_helpers import save_to_store, get_repository
        order_id = str(_uuid_mod.uuid4())
        order = {
            "id": order_id,
            "number": f"PA-{order_id[:8].upper()}",
            "status": "SUBMITTED",
            "created_at": now_iso(),
            "tenant_id": self.tenant_id,
            **body,
        }
        repo = doc_repo(self.db)
        repo.save("sales_order", order_id, order)
        return order

    def list_portal_contracts(self) -> list:
        try:
            contracts = list_docs(self.db, "kontrakt", limit=200, tenant_id=self.tenant_id)
        except Exception:
            contracts = []
        return [
            {
                "id": c.get("id", ""),
                "contract_number": c.get("nummer") or c.get("contract_number", ""),
                "article_name": c.get("artikel_name") or c.get("article_name", ""),
                "article_number": c.get("artikel_nummer") or c.get("article_number", ""),
                "contract_price": float(c.get("preis") or c.get("contract_price") or 0),
                "list_price": float(c.get("listenpreis") or c.get("list_price") or 0),
                "unit": c.get("einheit") or c.get("unit", "kg"),
                "total_quantity": float(c.get("gesamtmenge") or c.get("total_quantity") or 0),
                "remaining_quantity": float(c.get("verbleibende_menge") or c.get("remaining_quantity") or 0),
                "status": c.get("status", "ACTIVE"),
                "valid_until": c.get("laufzeit_bis") or c.get("valid_until", ""),
            }
            for c in contracts
        ]

    def list_portal_pre_purchases(self) -> list:
        try:
            pps = list_docs(self.db, "vorkauf", limit=200, tenant_id=self.tenant_id)
        except Exception:
            pps = []
        return [
            {
                "id": p.get("id", ""),
                "pre_purchase_number": p.get("nummer") or p.get("pre_purchase_number", ""),
                "article_name": p.get("artikel_name") or p.get("article_name", ""),
                "article_number": p.get("artikel_nummer") or p.get("article_number", ""),
                "pre_purchase_price": float(p.get("preis") or p.get("pre_purchase_price") or 0),
                "current_list_price": float(p.get("listenpreis") or p.get("current_list_price") or 0),
                "unit": p.get("einheit") or p.get("unit", "kg"),
                "total_quantity": float(p.get("gesamtmenge") or p.get("total_quantity") or 0),
                "remaining_quantity": float(p.get("verbleibende_menge") or p.get("remaining_quantity") or 0),
                "payment_date": p.get("zahldatum") or p.get("payment_date", ""),
                "valid_until": p.get("laufzeit_bis") or p.get("valid_until"),
            }
            for p in pps
        ]

    def list_portal_vertraege(self) -> list:
        try:
            items = self.db.query(Rahmenvertrag).order_by(Rahmenvertrag.laufzeit_bis.desc()).limit(500).all()
        except Exception:
            items = []
        return [
            {
                "id": i.id,
                "nummer": i.nummer,
                "typ": i.typ,
                "partner": i.partner,
                "laufzeitBis": i.laufzeit_bis.date().isoformat() if i.laufzeit_bis else None,
                "status": i.status,
            }
            for i in items
        ]

    def list_portal_zertifikate(self) -> list:
        try:
            items = self.db.query(ZertifikatEintrag).order_by(ZertifikatEintrag.gueltig_bis.desc()).limit(500).all()
        except Exception:
            items = []
        return [
            {
                "id": i.id,
                "art": i.art,
                "nummer": i.nummer,
                "gueltigBis": i.gueltig_bis.date().isoformat() if i.gueltig_bis else None,
                "status": i.status,
            }
            for i in items
        ]
