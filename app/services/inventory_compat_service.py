"""Service layer for compat inventory (lager) and futter domain routes."""
from __future__ import annotations

import csv
import io
import json
import logging
import uuid as _uuid_mod
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import Article as ArticleModel, InventoryCount
from app.domains.operations.models import Charge
from app.services.compat_helpers import (
    enqueue_event,
    list_docs,
    now_iso,
    doc_repo,
    safe_float,
)

logger = logging.getLogger(__name__)


class InventoryCompatService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Lager Dashboard ───────────────────────────────────────────────────────

    def get_lager_dashboard(self) -> dict:
        from sqlalchemy import text
        rows = self.db.execute(
            text("SELECT artikel_id, artikel_name, menge, einheit, lager_id "
                 "FROM lager_bestand WHERE tenant_id = :tid ORDER BY artikel_name"),
            {"tid": self.tenant_id},
        ).fetchall()
        items = [dict(r._mapping) for r in rows]
        total_value = sum(safe_float(i.get("menge")) for i in items)
        return {"bestand": items, "total_positions": len(items), "total_menge": total_value}

    # ── Einlagerung (FIFO/FEFO) ───────────────────────────────────────────────

    async def create_einlagerung(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "EINGELAGERT",
               "created_at": now_iso(), **payload}
        repo.save("lager_einlagerung", doc["id"], doc)
        await enqueue_event(self.db, event_type="lager.einlagerung.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    # ── Auslagerung ───────────────────────────────────────────────────────────

    async def create_auslagerung(self, payload: dict, strategy: str = "FIFO") -> dict:
        if strategy not in ("FIFO", "FEFO", "MANUAL"):
            raise ValidationFailedError(f"Unknown strategy: {strategy}")
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "AUSGELAGERT",
               "strategy": strategy, "created_at": now_iso(), **payload}
        repo.save("lager_auslagerung", doc["id"], doc)
        await enqueue_event(self.db, event_type="lager.auslagerung.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def list_auslagerungen(self) -> list:
        return list_docs(self.db, "lager_auslagerung", tenant_id=self.tenant_id)

    # ── Inventur ──────────────────────────────────────────────────────────────

    def list_inventuren(self) -> list:
        return list_docs(self.db, "inventur", tenant_id=self.tenant_id)

    async def create_inventur(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("inventur", doc["id"], doc)
        return doc

    def get_inventur(self, inventur_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("inventur", inventur_id)
        if doc is None:
            raise EntityNotFoundError(f"Inventur {inventur_id} not found")
        return doc

    # ── InventoryCount (DB-backed) ────────────────────────────────────────────

    def list_inventur_counts(self) -> dict:
        items = self.db.query(InventoryCount).order_by(InventoryCount.created_at.desc()).limit(500).all()
        return {
            "items": [
                {
                    "id": i.id,
                    "lager": i.warehouse_id,
                    "status": i.status,
                    "expected": int(i.total_items or 0),
                    "counted": int(i.total_items or 0),
                    "differenz": int(i.discrepancies_found or 0),
                }
                for i in items
            ],
            "total": len(items),
        }

    def complete_inventur_counts(self, ids: list) -> dict:
        if not ids:
            return {"ok": True, "updated": 0}
        updated = (
            self.db.query(InventoryCount)
            .filter(InventoryCount.id.in_(ids))
            .update({InventoryCount.status: "completed"}, synchronize_session=False)
        )
        self.db.commit()
        return {"ok": True, "updated": int(updated)}

    def delete_inventur_count(self, item_id: str) -> None:
        row = self.db.query(InventoryCount).filter(InventoryCount.id == item_id).first()
        if not row:
            raise EntityNotFoundError(f"Inventur-Eintrag {item_id} nicht gefunden")
        self.db.delete(row)
        self.db.commit()

    # ── MHD / Lot analytics ───────────────────────────────────────────────────

    def get_mhd_warnings(self) -> dict:
        items = self.db.query(Charge).filter(Charge.tenant_id == self.tenant_id).order_by(Charge.eingang.asc()).limit(200).all()
        return {
            "items": [
                {
                    "id": c.id,
                    "article": c.artikel,
                    "batch": c.chargen_id,
                    "bestBefore": c.freigabe_datum.isoformat()[:10] if c.freigabe_datum else None,
                    "stock": float(c.menge or 0),
                }
                for c in items
            ]
        }

    def get_top_sellers(self) -> dict:
        items = (
            self.db.query(ArticleModel)
            .filter(ArticleModel.is_active == True)  # noqa: E712
            .order_by(ArticleModel.sales_price.desc())
            .limit(50)
            .all()
        )
        return {
            "items": [
                {"articleId": a.id, "article": a.name, "value": float(a.sales_price or 0), "unit": a.unit}
                for a in items
            ]
        }

    def get_slow_movers(self) -> dict:
        items = (
            self.db.query(ArticleModel)
            .filter(ArticleModel.is_active == True)  # noqa: E712
            .order_by(ArticleModel.sales_price.asc())
            .limit(50)
            .all()
        )
        return {
            "items": [
                {"articleId": a.id, "article": a.name, "value": float(a.sales_price or 0), "unit": a.unit}
                for a in items
            ]
        }

    def list_lots(self, search: Optional[str] = None) -> dict:
        query = self.db.query(Charge).filter(Charge.tenant_id == self.tenant_id)
        if search:
            like = f"%{search}%"
            query = query.filter((Charge.chargen_id.ilike(like)) | (Charge.artikel.ilike(like)))
        items = query.order_by(Charge.eingang.desc()).limit(200).all()
        return {
            "items": [
                {
                    "id": c.id,
                    "lotId": c.chargen_id,
                    "article": c.artikel,
                    "articleId": c.artikel_id,
                    "quantity": float(c.menge or 0),
                    "location": c.lagerort,
                    "status": c.status,
                }
                for c in items
            ],
            "total": len(items),
        }

    def get_lot(self, lot_id: str) -> dict:
        lot = self.db.query(Charge).filter(
            Charge.tenant_id == self.tenant_id,
            (Charge.id == lot_id) | (Charge.chargen_id == lot_id),
        ).first()
        if not lot:
            raise EntityNotFoundError(f"Lot {lot_id} not found")
        return {
            "id": lot.id,
            "lotId": lot.chargen_id,
            "article": lot.artikel,
            "articleId": lot.artikel_id,
            "quantity": float(lot.menge or 0),
            "location": lot.lagerort,
            "status": lot.status,
            "qualityStatus": lot.qualitaetsstatus,
            "origin": lot.herkunft,
            "events": [
                {"type": "eingang", "date": lot.eingang.isoformat() if lot.eingang else None, "note": "Wareneingang erfasst"},
                {"type": "update", "date": lot.updated_at.isoformat() if lot.updated_at else None, "note": "Letzte Aktualisierung"},
            ],
        }

    async def abschliessen_inventur(self, inventur_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("inventur", inventur_id)
        if doc is None:
            raise EntityNotFoundError(f"Inventur {inventur_id} not found")
        if doc.get("status") == "ABGESCHLOSSEN":
            from app.core.exceptions import ConflictError
            raise ConflictError("Inventur already closed")
        doc["status"] = "ABGESCHLOSSEN"
        doc["abgeschlossen_at"] = now_iso()
        repo.save("inventur", inventur_id, doc)
        await enqueue_event(self.db, event_type="inventur.abgeschlossen",
                            aggregate_id=inventur_id, payload=doc, tenant_id=self.tenant_id)
        return doc


class FutterCompatService:
    """Service for futter (animal feed) domain routes."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Futterarten & Rationen ────────────────────────────────────────────────

    def list_futterarten(self) -> list:
        return list_docs(self.db, "futterart", tenant_id=self.tenant_id)

    def get_futterart(self, futterart_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("futterart", futterart_id)
        if doc is None:
            raise EntityNotFoundError(f"Futterart {futterart_id} not found")
        return doc

    async def create_futterart(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "created_at": now_iso(), **payload}
        repo.save("futterart", doc["id"], doc)
        return doc

    def update_futterart(self, futterart_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("futterart", futterart_id)
        if doc is None:
            raise EntityNotFoundError(f"Futterart {futterart_id} not found")
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("futterart", futterart_id, doc)
        return doc

    def delete_futterart(self, futterart_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("futterart", futterart_id)
        if doc is None:
            raise EntityNotFoundError(f"Futterart {futterart_id} not found")
        repo.delete("futterart", futterart_id)
        return {"deleted": True, "id": futterart_id}

    def list_rationen(self) -> list:
        return list_docs(self.db, "ration", tenant_id=self.tenant_id)

    def get_ration(self, ration_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("ration", ration_id)
        if doc is None:
            raise EntityNotFoundError(f"Ration {ration_id} not found")
        return doc

    async def create_ration(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "created_at": now_iso(), **payload}
        repo.save("ration", doc["id"], doc)
        await enqueue_event(self.db, event_type="ration.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def update_ration(self, ration_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("ration", ration_id)
        if doc is None:
            raise EntityNotFoundError(f"Ration {ration_id} not found")
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("ration", ration_id, doc)
        return doc

    # ── DLG Nährwertberechnung (503/504) ─────────────────────────────────────

    def berechne_naehrwerte(self, ration_id: str) -> dict:
        """Compute DLG nutrient values for a ration."""
        ration = self.get_ration(ration_id)
        komponenten = ration.get("komponenten", [])
        totals: dict[str, float] = {
            "rohprotein_g": 0.0, "rohfaser_g": 0.0, "rohfett_g": 0.0,
            "staerke_g": 0.0, "zucker_g": 0.0, "nel_mj": 0.0,
            "me_mj": 0.0, "tm_kg": 0.0,
        }
        for k in komponenten:
            menge = safe_float(k.get("menge_kg", 0))
            nw = k.get("naehrwerte", {})
            for key in totals:
                totals[key] += menge * safe_float(nw.get(key, 0))
        return {"ration_id": ration_id, "naehrwerte": totals,
                "komponenten_count": len(komponenten), "calculated_at": now_iso()}

    # ── ArticleModel-backed lists ─────────────────────────────────────────────

    def list_einzelfuttermittel(self) -> list:
        items = self.db.query(ArticleModel).filter(ArticleModel.is_active == True).limit(500).all()  # noqa: E712
        return [
            {
                "id": i.id,
                "name": i.name,
                "artikelnummer": i.article_number,
                "kategorie": i.category,
                "protein": float((getattr(i, "custom_properties", None) or {}).get("protein", 0)),
                "energie": float((getattr(i, "custom_properties", None) or {}).get("energie", 0)),
                "preis": float(i.sales_price or 0),
                "einheit": i.unit,
            }
            for i in items
        ]

    def list_mischfuttermittel(self) -> list:
        items = self.db.query(ArticleModel).filter(ArticleModel.is_active == True).limit(200).all()  # noqa: E712
        return [
            {
                "id": i.id,
                "name": i.name,
                "artikelnummer": i.article_number,
                "komponenten": int((getattr(i, "custom_properties", None) or {}).get("komponenten", 0)),
                "preis": float(i.sales_price or 0),
                "einheit": i.unit,
            }
            for i in items
        ]

    def soft_delete_artikel(self, ids: list, tenant_id: Optional[str] = None) -> dict:
        if not ids:
            raise ValidationFailedError("Keine Futtermittel-IDs übergeben")
        query = self.db.query(ArticleModel).filter(ArticleModel.id.in_(ids))
        if hasattr(ArticleModel, "tenant_id") and tenant_id:
            query = query.filter(
                (ArticleModel.tenant_id == tenant_id) | (ArticleModel.tenant_id.is_(None))
            )
        articles = query.all()
        articles_by_id = {str(a.id): a for a in articles}
        deleted, errors, missing_ids = 0, [], []
        for item_id in ids:
            article = articles_by_id.get(item_id)
            if article is None:
                missing_ids.append(item_id)
                continue
            try:
                article.is_active = False
                deleted += 1
            except Exception as exc:
                errors.append({"id": item_id, "detail": str(exc)})
        if deleted > 0:
            self.db.commit()
        return {"requested": len(ids), "deleted": deleted, "missing_ids": missing_ids, "errors": errors}

    # ── Charge-backed lists ───────────────────────────────────────────────────

    def list_chargen(self) -> list:
        lots = self.db.query(Charge).filter(Charge.tenant_id == self.tenant_id).order_by(Charge.eingang.desc()).limit(500).all()
        return [
            {
                "id": c.id,
                "chargen_id": c.chargen_id,
                "artikel": c.artikel,
                "menge": float(c.menge or 0),
                "status": c.status,
                "eingang": c.eingang.isoformat() if c.eingang else None,
            }
            for c in lots
        ]

    def list_qualitaetskontrolle(self) -> list:
        lots = self.db.query(Charge).filter(Charge.tenant_id == self.tenant_id).order_by(Charge.updated_at.desc()).limit(500).all()
        return [
            {
                "id": c.id,
                "charge": c.chargen_id,
                "artikel": c.artikel,
                "qualitaetsstatus": c.qualitaetsstatus,
                "freigabe_datum": c.freigabe_datum.isoformat() if c.freigabe_datum else None,
                "status": c.status,
            }
            for c in lots
        ]

    def get_statistik(self) -> dict:
        lots = self.db.query(Charge).filter(Charge.tenant_id == self.tenant_id).all()
        return {
            "gesamtChargen": len(lots),
            "gesamtMenge": round(sum(float(c.menge or 0) for c in lots), 3),
            "freigegeben": sum(1 for c in lots if c.status == "freigegeben"),
            "inPruefung": sum(1 for c in lots if c.status == "in-pruefung"),
            "gesperrt": sum(1 for c in lots if c.status == "gesperrt"),
        }

    # ── SQL CSV Imports ───────────────────────────────────────────────────────

    def import_einzelfuttermittel_sql(self, rows: list) -> dict:
        from sqlalchemy import text
        created, errors = 0, []
        for i, row in enumerate(rows):
            norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
            name = norm.get("name") or norm.get("artikel") or norm.get("bezeichnung", "")
            if not name:
                errors.append(f"Zeile {i+2}: Name fehlt")
                continue
            try:
                self.db.execute(
                    text("""INSERT INTO domain_inventory.articles
                            (id, name, article_number, unit, is_active, created_at)
                            VALUES (:id, :name, :artnr, 'kg', true, NOW())
                            ON CONFLICT DO NOTHING"""),
                    {"id": str(_uuid_mod.uuid4()), "name": name,
                     "artnr": norm.get("artikelnummer") or norm.get("artnr", "")},
                )
                created += 1
            except Exception as exc:
                errors.append(f"Zeile {i+2}: {str(exc)[:80]}")
        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            return {"created": 0, "updated": 0, "errors": [str(exc)]}
        return {"created": created, "updated": 0, "errors": errors}

    def import_mischfuttermittel_sql(self, rows: list) -> dict:
        from sqlalchemy import text
        created, errors = 0, []
        for i, row in enumerate(rows):
            norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
            name = norm.get("name") or norm.get("bezeichnung", "")
            if not name:
                errors.append(f"Zeile {i+2}: Name fehlt")
                continue
            props = {k: v for k, v in norm.items() if k in ("tierart", "lebensphase", "typ", "futtergruppe")}
            try:
                self.db.execute(
                    text("""INSERT INTO domain_inventory.articles
                            (id, name, article_number, unit, is_active, custom_properties, created_at)
                            VALUES (:id, :name, :artnr, 'kg', true, :props::jsonb, NOW())
                            ON CONFLICT DO NOTHING"""),
                    {"id": str(_uuid_mod.uuid4()), "name": name,
                     "artnr": norm.get("artikelnummer", ""),
                     "props": json.dumps(props)},
                )
                created += 1
            except Exception as exc:
                errors.append(f"Zeile {i+2}: {str(exc)[:80]}")
        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            return {"created": 0, "updated": 0, "errors": [str(exc)]}
        return {"created": created, "updated": 0, "errors": errors}

    def import_chargen_sql(self, rows: list) -> dict:
        from sqlalchemy import text
        created, errors = 0, []
        for i, row in enumerate(rows):
            norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
            artikel = norm.get("artikel") or norm.get("name", "")
            if not artikel:
                errors.append(f"Zeile {i+2}: Artikel fehlt")
                continue
            try:
                self.db.execute(
                    text("""INSERT INTO domain_ops.ops_chargen
                            (id, chargen_id, artikel, menge, status, qualitaetsstatus, eingang, created_at)
                            VALUES (:id, :cid, :artikel, :menge, 'eingang', 'offen', NOW(), NOW())
                            ON CONFLICT DO NOTHING"""),
                    {"id": str(_uuid_mod.uuid4()),
                     "cid": norm.get("chargen_id") or norm.get("charge") or str(_uuid_mod.uuid4())[:8].upper(),
                     "artikel": artikel,
                     "menge": float(norm.get("menge", 0) or 0)},
                )
                created += 1
            except Exception as exc:
                errors.append(f"Zeile {i+2}: {str(exc)[:80]}")
        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            return {"created": 0, "updated": 0, "errors": [str(exc)]}
        return {"created": created, "updated": 0, "errors": errors}

    # ── CSV Import (doc_repo legacy) ──────────────────────────────────────────

    def import_futterarten_csv(self, csv_content: str) -> dict:
        reader = csv.DictReader(io.StringIO(csv_content))
        imported, errors = [], []
        repo = doc_repo(self.db)
        for i, row in enumerate(reader):
            try:
                doc_id = row.get("id") or uuid7()
                doc = {"id": doc_id, "tenantId": self.tenant_id,
                       "created_at": now_iso(), **row}
                repo.save("futterart", doc_id, doc)
                imported.append(doc_id)
            except Exception as exc:
                errors.append({"row": i + 1, "error": str(exc)})
        return {"imported": len(imported), "errors": errors}
