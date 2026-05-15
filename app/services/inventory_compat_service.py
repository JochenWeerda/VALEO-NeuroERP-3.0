"""Service layer for compat inventory (lager) and futter domain routes."""
from __future__ import annotations

import csv
import io
import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
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

    # ── CSV Import ────────────────────────────────────────────────────────────

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
