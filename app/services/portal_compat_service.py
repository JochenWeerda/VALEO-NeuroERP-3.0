"""Service layer for compat portal domain routes (supplier/customer portal)."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import Article as ArticleModel
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class PortalCompatService:
    def __init__(self, db: Session, tenant_id: str, customer_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id
        # Das Kundenkonto aus ``app.auth.portal_kunde`` (TENANT-DOC-001). Ohne Kunden liefern die Portal-Listen
        # nichts: bis 14.10.2026 sah jede angemeldete Person die Belege aller Kunden des Mandanten.
        self.customer_id = customer_id

    def _kundenbelege(self, doc_type: str, limit: int) -> list:
        if not self.customer_id:
            return []
        return list_docs(self.db, doc_type, limit=limit, tenant_id=self.tenant_id, customer_id=self.customer_id)

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
            raise EntityNotFoundError("Portal order", order_id)
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
            raise EntityNotFoundError("Portal order", order_id)
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("portal_order", order_id, doc)
        return doc

    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_order", order_id)
        if doc is None:
            raise EntityNotFoundError("Portal order", order_id)
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
            raise EntityNotFoundError("Product", product_id)
        return doc

    # ── Contracts ─────────────────────────────────────────────────────────────

    def list_contracts(self) -> list:
        return list_docs(self.db, "portal_contract", tenant_id=self.tenant_id)

    def get_contract(self, contract_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_contract", contract_id)
        if doc is None:
            raise EntityNotFoundError("Contract", contract_id)
        return doc

    # ── Invoices ──────────────────────────────────────────────────────────────

    def list_invoices(self) -> list:
        return list_docs(self.db, "portal_invoice", tenant_id=self.tenant_id)

    def get_invoice(self, invoice_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_invoice", invoice_id)
        if doc is None:
            raise EntityNotFoundError("Invoice", invoice_id)
        return doc

    # ── Notifications ─────────────────────────────────────────────────────────

    def list_notifications(self) -> list:
        return list_docs(self.db, "portal_notification", tenant_id=self.tenant_id)

    def mark_notification_read(self, notification_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("portal_notification", notification_id)
        if doc is None:
            raise EntityNotFoundError("Notification", notification_id)
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

    def get_portal_dashboard_full(self, rechte: Optional[frozenset] = None) -> dict:
        """Startseite — nur die Kacheln, die die Portalrolle sehen darf (``app/auth/portal_kunde.PORTAL_RECHTE``).

        Ohne ``rechte`` (interne Aufrufe) alles.
        """
        verkauf = rechte is None or "verkauf" in rechte
        finanzen = rechte is None or "finanzen" in rechte
        orders = self._kundenbelege("sales_order", 20) if verkauf else []
        invoices = self._kundenbelege("sales_invoice", 20) if finanzen else []
        docs = self._kundendokumente() if finanzen else []
        offene_rechnungen = sum(1 for i in invoices if str(i.get("status", "")).lower() in {"offen", "ueberfaellig"})
        kpis = []
        if verkauf:
            kpis.append({"label": "Bestellungen", "value": str(len(orders))})
        if finanzen:
            kpis.append({"label": "Rechnungen offen", "value": str(offene_rechnungen)})
            kpis.append({"label": "Dokumente", "value": str(len(docs))})
        return {
            "kpis": kpis,
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
        docs = self._kundenbelege("customer_inquiry", 500)
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
        docs = self._kundenbelege("sales_order", 500)
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

    def _kundendokumente(self) -> list:
        """Dokumente, Rahmenvertraege und Zertifikate (``domain_ops``) tragen weder Mandant noch Kunde.

        Bis 14.10.2026 zeigte das Portal sie jedem — interne Betriebsunterlagen aller Haeuser. Solange keiner dieser
        Eintraege einem Kunden zugeordnet ist, gehoert keiner ins Portal (TENANT-DOC-001).
        """
        return []

    def list_portal_dokumente(self) -> list:
        docs = self._kundendokumente()
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

    def list_portal_feldbuch(self, schlag_ids: Optional[tuple] = None) -> list:
        """``schlag_ids``: zugewiesene Schlaege eines Mitarbeiters; dann ohne Rueckfall auf Lieferscheine."""
        from app.infrastructure.models.agrar_models import FeldbuchSchlag
        if not self.tenant_id or not self.customer_id:
            return []
        abfrage = self.db.query(FeldbuchSchlag).filter(
            FeldbuchSchlag.tenant_id == self.tenant_id, FeldbuchSchlag.customer_id == self.customer_id)
        if schlag_ids is not None:
            abfrage = abfrage.filter(FeldbuchSchlag.id.in_(list(schlag_ids)))
        schlaege = abfrage.order_by(FeldbuchSchlag.name).all()
        if schlag_ids is not None and not schlaege:
            return []
        if schlaege:
            return [
                {"id": s.id, "schlag": s.name, "kultur": s.kultur or "",
                 "flaeche": s.flaeche, "letzteMassnahme": None, "naechsteMassnahme": None}
                for s in schlaege
            ]
        deliveries = self._kundenbelege("sales_delivery", 1000)
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
        deliveries = self._kundenbelege("sales_delivery", 2000)
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
        invoices = self._kundenbelege("sales_invoice", 500)
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
        # Der Katalog gehoert dem Mandanten; bis 14.10.2026 las diese Liste die Artikel aller Mandanten.
        articles = (
            self.db.query(ArticleModel)
            .filter(ArticleModel.tenant_id == self.tenant_id, ArticleModel.is_active == True)  # noqa: E712
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

    def list_portal_vertraege(self) -> list:
        items = self._kundendokumente()
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
        items = self._kundendokumente()
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
