"""Service layer for compat Annahme (goods intake) and LKW queue routes."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import Article as ArticleModel, LkwAnnahmeQueue
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class AnnahmeService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── LKW Queue ─────────────────────────────────────────────────────────────

    def list_lkw_queue(self) -> list:
        return list_docs(self.db, "lkw_queue", tenant_id=self.tenant_id)

    def get_lkw_entry(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        return doc

    async def register_lkw(self, payload: dict) -> dict:
        """Register a truck in the intake queue, resolving article reference."""
        artikel_id = payload.get("artikel_id")
        if not artikel_id:
            artikel_name = payload.get("artikel_name", "")
            if artikel_name:
                artikel_id = await self._resolve_article(artikel_name)
        repo = doc_repo(self.db)
        doc = {
            "id": uuid7(),
            "tenantId": self.tenant_id,
            "status": "WARTEND",
            "artikel_id": artikel_id,
            "created_at": now_iso(),
            **{k: v for k, v in payload.items() if k != "artikel_id"},
        }
        repo.save("lkw_queue", doc["id"], doc)
        await enqueue_event(self.db, event_type="lkw.registered",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    async def _resolve_article(self, artikel_name: str) -> Optional[str]:
        from sqlalchemy import text
        row = self.db.execute(
            text("SELECT id FROM artikel WHERE name ILIKE :name AND tenant_id = :tid LIMIT 1"),
            {"name": f"%{artikel_name}%", "tid": self.tenant_id},
        ).fetchone()
        return str(row[0]) if row else None

    def call_lkw(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        if doc.get("status") != "WARTEND":
            raise ConflictError(f"Cannot call LKW in status '{doc.get('status')}'")
        doc["status"] = "GERUFEN"
        doc["called_at"] = now_iso()
        repo.save("lkw_queue", entry_id, doc)
        return doc

    def complete_lkw(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        doc["status"] = "ABGEFERTIGT"
        doc["completed_at"] = now_iso()
        repo.save("lkw_queue", entry_id, doc)
        return doc

    def remove_lkw(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        repo.delete("lkw_queue", entry_id)
        return {"deleted": True, "id": entry_id}

    # ── LKW Queue — DB-backed (LkwAnnahmeQueue ORM) ──────────────────────────

    @staticmethod
    def _lkw_row_to_dict(row: LkwAnnahmeQueue, position: int = 0) -> dict:
        ankunftszeit = row.ankunftszeit
        wartezeit_min = 0
        if ankunftszeit:
            now_utc = datetime.now(timezone.utc)
            arr_utc = ankunftszeit.astimezone(timezone.utc) if ankunftszeit.tzinfo else ankunftszeit.replace(tzinfo=timezone.utc)
            wartezeit_min = max(0, int((now_utc - arr_utc).total_seconds() / 60))
        status = row.status or "wartend"
        if status == "warteschlange":
            status = "wartend"
        return {
            "id": row.id,
            "position": position,
            "kennzeichen": row.kennzeichen or "",
            "lieferant": row.lieferant or "",
            "article_id": row.article_id,
            "artikel": row.artikel or "",
            "ankunft": ankunftszeit.isoformat() if ankunftszeit else "",
            "wartezeit": wartezeit_min,
            "status": status,
            "lieferschein_nr": row.lieferschein_nr or "",
            "klaerung": row.klaerung or None,
        }

    def list_lkw_db(self) -> dict:
        try:
            rows = (
                self.db.query(LkwAnnahmeQueue)
                .filter(LkwAnnahmeQueue.tenant_id == self.tenant_id)
                .order_by(LkwAnnahmeQueue.ankunftszeit.asc())
                .all()
            )
        except Exception:
            return {"items": [], "total": 0}
        items = [self._lkw_row_to_dict(r, i + 1) for i, r in enumerate(rows)]
        return {"items": items, "total": len(items)}

    def get_lkw_db(self, reg_id: str) -> dict:
        row = (
            self.db.query(LkwAnnahmeQueue)
            .filter(LkwAnnahmeQueue.id == reg_id, LkwAnnahmeQueue.tenant_id == self.tenant_id)
            .first()
        )
        if not row:
            raise EntityNotFoundError(f"LKW-Eintrag {reg_id} nicht gefunden")
        return self._lkw_row_to_dict(row, position=0)

    def patch_lkw_db(self, reg_id: str, status: Optional[str], klaerung: Optional[dict]) -> dict:
        if status is None and klaerung is None:
            raise ValidationFailedError("status oder klaerung muss angegeben werden")
        if status is not None and status not in ("in-bearbeitung", "abgeschlossen", "gesperrt"):
            raise ValidationFailedError("status muss 'in-bearbeitung', 'abgeschlossen' oder 'gesperrt' sein")
        row = (
            self.db.query(LkwAnnahmeQueue)
            .filter(LkwAnnahmeQueue.id == reg_id, LkwAnnahmeQueue.tenant_id == self.tenant_id)
            .first()
        )
        if not row:
            raise EntityNotFoundError(f"LKW-Eintrag {reg_id} nicht gefunden")
        if status is not None:
            row.status = status
        if klaerung is not None:
            existing = row.klaerung or {}
            if not isinstance(existing, dict):
                existing = {}
            existing.update(klaerung)
            existing.setdefault("updated_at", datetime.utcnow().isoformat())
            row.klaerung = existing
        self.db.commit()
        self.db.refresh(row)
        return self._lkw_row_to_dict(row, position=0)

    def repair_article_db(self, reg_id: str) -> dict:
        row = (
            self.db.query(LkwAnnahmeQueue)
            .filter(LkwAnnahmeQueue.id == reg_id, LkwAnnahmeQueue.tenant_id == self.tenant_id)
            .first()
        )
        if not row:
            raise EntityNotFoundError(f"LKW-Eintrag {reg_id} nicht gefunden")
        if row.article_id:
            return {"status": "already_set", "article_id": row.article_id, "artikel": row.artikel}

        article_id, label, reason = self._repair_article_reference(row.artikel)
        if not article_id:
            return {"status": "not_resolved", "reason": reason}
        row.article_id = article_id
        row.artikel = label
        self.db.commit()
        self.db.refresh(row)
        return {"status": "updated", "article_id": article_id, "artikel": label}

    def _repair_article_reference(self, artikel: Optional[str]):
        label = (artikel or "").strip()
        if not label:
            return None, None, "missing_label"
        base = self.db.query(ArticleModel).filter(
            ArticleModel.is_active == True,  # noqa: E712
            (ArticleModel.tenant_id == self.tenant_id) | (ArticleModel.tenant_id.is_(None)),
        )
        by_num = base.filter(ArticleModel.article_number == label).all()
        if len(by_num) == 1:
            a = by_num[0]
            return str(a.id), a.name or a.article_number or label, "article_number"
        if len(by_num) > 1:
            return None, None, "ambiguous_article_number"
        by_name = base.filter(ArticleModel.name == label).all()
        if len(by_name) == 1:
            a = by_name[0]
            return str(a.id), a.name or a.article_number or label, "article_name"
        if len(by_name) > 1:
            return None, None, "ambiguous_article_name"
        return None, None, "not_found"

    def _resolve_article_reference(self, article_id: Optional[str], artikel: Optional[str]):
        base = self.db.query(ArticleModel).filter(
            ArticleModel.is_active == True,  # noqa: E712
            (ArticleModel.tenant_id == self.tenant_id) | (ArticleModel.tenant_id.is_(None)),
        )
        candidate_id = (article_id or "").strip() or None
        candidate_label = (artikel or "").strip()
        article = None
        if candidate_id:
            article = base.filter(ArticleModel.id == candidate_id).first()
            if article is None:
                article = base.filter(ArticleModel.article_number == candidate_id).first()
        if article is None and candidate_label:
            article = (
                base.filter(
                    (ArticleModel.article_number == candidate_label) | (ArticleModel.name == candidate_label)
                )
                .order_by(ArticleModel.name.asc())
                .first()
            )
        if article is None:
            return candidate_id, candidate_label
        return str(article.id), article.name or article.article_number or candidate_label or str(article.id)

    def register_lkw_db(self, payload: Any) -> dict:
        """Register a truck using the LkwAnnahmeQueue ORM model."""
        reg_id = uuid7()
        ankunft_dt = None
        ankunftszeit_str = getattr(payload, "ankunftszeit", None) or ""
        if ankunftszeit_str:
            try:
                normalized = ankunftszeit_str.replace("Z", "+00:00")[:19]
                ankunft_dt = datetime.fromisoformat(normalized)
                if ankunft_dt.tzinfo is None:
                    ankunft_dt = ankunft_dt.replace(tzinfo=timezone.utc)
            except Exception:  # noqa: BLE001 — Ankunfts-Datetime-Parsing fehlgeschlagen; Rohwert bleibt
                pass
        resolved_id, resolved_label = self._resolve_article_reference(
            getattr(payload, "article_id", None), getattr(payload, "artikel", None)
        )
        row = LkwAnnahmeQueue(
            id=reg_id,
            tenant_id=self.tenant_id,
            kennzeichen=getattr(payload, "kennzeichen", ""),
            lieferant=getattr(payload, "lieferant", ""),
            lieferschein_nr=getattr(payload, "lieferschein_nr", "") or "",
            article_id=resolved_id,
            artikel=resolved_label,
            ankunftszeit=ankunft_dt,
            prioritaet=getattr(payload, "prioritaet", "normal"),
            status="wartend",
            attachment_ids=getattr(payload, "attachment_ids", None) or [],
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return {
            "id": reg_id,
            "kennzeichen": row.kennzeichen,
            "article_id": resolved_id,
            "artikel": resolved_label,
            "status": "wartend",
        }

    # ── Qualitaets-Check ──────────────────────────────────────────────────────

    def list_qualitaets_checks(self) -> list:
        return list_docs(self.db, "qualitaets_check", tenant_id=self.tenant_id)

    async def create_qualitaets_check(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("qualitaets_check", doc["id"], doc)
        await enqueue_event(self.db, event_type="qualitaets_check.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def get_qualitaets_check(self, check_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("qualitaets_check", check_id)
        if doc is None:
            raise EntityNotFoundError(f"Qualitaets-Check {check_id} not found")
        return doc

    async def complete_qualitaets_check(self, check_id: str, result: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("qualitaets_check", check_id)
        if doc is None:
            raise EntityNotFoundError(f"Qualitaets-Check {check_id} not found")
        doc["status"] = "ABGESCHLOSSEN"
        doc["result"] = result
        doc["completed_at"] = now_iso()
        repo.save("qualitaets_check", check_id, doc)
        await enqueue_event(self.db, event_type="qualitaets_check.completed",
                            aggregate_id=check_id, payload=doc, tenant_id=self.tenant_id)
        return doc
