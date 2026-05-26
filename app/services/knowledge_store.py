"""
Knowledge Store — NC-06
Persistenter Store fuer Business-Wissen, Prompt-Templates und Regeln.
Ergaenzt die bestehende Policy Registry um einen allgemeinen Wissens-Store.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class KnowledgeType(str, Enum):
    PROMPT_TEMPLATE = "prompt_template"
    BUSINESS_RULE = "business_rule"
    FAQ = "faq"
    PROCESS_DESCRIPTION = "process_description"
    DOMAIN_GLOSSARY = "domain_glossary"


@dataclass
class KnowledgeEntry:
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    knowledge_type: KnowledgeType = KnowledgeType.BUSINESS_RULE
    domain: str = ""
    key: str = ""
    title: str = ""
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "knowledge_type": self.knowledge_type.value,
            "domain": self.domain,
            "key": self.key,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "version": self.version,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


_IN_MEMORY_STORE: dict[str, KnowledgeEntry] = {}


def _store_key(tenant_id: str, domain: str, key: str) -> str:
    return f"{tenant_id}:{domain}:{key}"


def store_knowledge(
    db: Optional[Session],
    entry: KnowledgeEntry,
    tenant_id: str = "system",
) -> KnowledgeEntry:
    store_key = _store_key(tenant_id, entry.domain, entry.key)

    if db:
        try:
            existing = db.execute(text(
                "SELECT version FROM domain_shared.knowledge_store "
                "WHERE key = :key AND domain = :domain AND tenant_id = :tid AND active = true"
            ), {"key": entry.key, "domain": entry.domain, "tid": tenant_id}).fetchone()

            if existing:
                entry.version = existing[0] + 1
                db.execute(text(
                    "UPDATE domain_shared.knowledge_store SET active = false "
                    "WHERE key = :key AND domain = :domain AND tenant_id = :tid AND active = true"
                ), {"key": entry.key, "domain": entry.domain, "tid": tenant_id})

            db.execute(text("""
                INSERT INTO domain_shared.knowledge_store
                (id, knowledge_type, domain, key, title, content, metadata, version, active, tenant_id, created_at, updated_at)
                VALUES (:id, :ktype, :domain, :key, :title, :content, :metadata, :version, :active, :tid, NOW(), NOW())
            """), {
                "id": entry.entry_id,
                "ktype": entry.knowledge_type.value,
                "domain": entry.domain,
                "key": entry.key,
                "title": entry.title,
                "content": entry.content,
                "metadata": json.dumps(entry.metadata),
                "version": entry.version,
                "active": entry.active,
                "tid": tenant_id,
            })
            db.commit()
            _IN_MEMORY_STORE.pop(store_key, None)
        except Exception as exc:
            logger.warning("DB knowledge store failed, using in-memory: %s", exc)
            existing = _IN_MEMORY_STORE.get(store_key)
            if existing is not None:
                entry.version = existing.version + 1
            _IN_MEMORY_STORE[store_key] = entry
    else:
        existing = _IN_MEMORY_STORE.get(store_key)
        if existing is not None:
            entry.version = existing.version + 1
        _IN_MEMORY_STORE[store_key] = entry

    return entry


def get_knowledge(
    db: Optional[Session],
    domain: str,
    key: str,
    tenant_id: str = "system",
) -> Optional[KnowledgeEntry]:
    if db:
        try:
            row = db.execute(text(
                "SELECT id, knowledge_type, domain, key, title, content, metadata, version, active, created_at, updated_at "
                "FROM domain_shared.knowledge_store WHERE key = :key AND domain = :domain AND active = true AND tenant_id = :tid"
            ), {"key": key, "domain": domain, "tid": tenant_id}).fetchone()
            if row:
                return KnowledgeEntry(
                    entry_id=str(row[0]),
                    knowledge_type=KnowledgeType(row[1]),
                    domain=row[2],
                    key=row[3],
                    title=row[4],
                    content=row[5],
                    metadata=json.loads(row[6]) if isinstance(row[6], str) else (row[6] or {}),
                    version=row[7],
                    active=row[8],
                    created_at=str(row[9]),
                    updated_at=str(row[10]),
                )
        except Exception:  # noqa: BLE001 — Knowledge-Store-Abfrage fehlgeschlagen; Standardwert wird zurückgegeben
            pass

    return _IN_MEMORY_STORE.get(_store_key(tenant_id, domain, key))


def search_knowledge(
    db: Optional[Session],
    domain: Optional[str] = None,
    knowledge_type: Optional[KnowledgeType] = None,
    query: Optional[str] = None,
    tenant_id: str = "system",
    limit: int = 50,
) -> list[KnowledgeEntry]:
    if db:
        try:
            conditions = ["active = true", "tenant_id = :tid"]
            params: dict[str, Any] = {"tid": tenant_id, "lim": limit}

            if domain:
                conditions.append("domain = :domain")
                params["domain"] = domain
            if knowledge_type:
                conditions.append("knowledge_type = :ktype")
                params["ktype"] = knowledge_type.value
            if query:
                conditions.append("(title ILIKE :q OR content ILIKE :q OR key ILIKE :q)")
                params["q"] = f"%{query}%"

            where = " AND ".join(conditions)
            rows = db.execute(text(
                f"SELECT id, knowledge_type, domain, key, title, content, metadata, version, active, created_at, updated_at "
                f"FROM domain_shared.knowledge_store WHERE {where} ORDER BY updated_at DESC LIMIT :lim"
            ), params).fetchall()

            return [
                KnowledgeEntry(
                    entry_id=str(r[0]),
                    knowledge_type=KnowledgeType(r[1]),
                    domain=r[2],
                    key=r[3],
                    title=r[4],
                    content=r[5],
                    metadata=json.loads(r[6]) if isinstance(r[6], str) else (r[6] or {}),
                    version=r[7],
                    active=r[8],
                    created_at=str(r[9]),
                    updated_at=str(r[10]),
                )
                for r in rows
            ]
        except Exception:  # noqa: BLE001 — Knowledge-Store-Abfrage fehlgeschlagen; Standardwert wird zurückgegeben
            pass

    results = [
        entry
        for key, entry in _IN_MEMORY_STORE.items()
        if key.startswith(f"{tenant_id}:")
    ]
    if domain:
        results = [e for e in results if e.domain == domain]
    if knowledge_type:
        results = [e for e in results if e.knowledge_type == knowledge_type]
    if query:
        q = query.lower()
        results = [e for e in results if q in e.title.lower() or q in e.content.lower()]
    return results[:limit]


def delete_knowledge(
    db: Optional[Session],
    domain: str,
    key: str,
    tenant_id: str = "system",
) -> bool:
    if db:
        try:
            result = db.execute(text(
                "UPDATE domain_shared.knowledge_store SET active = false, updated_at = NOW() "
                "WHERE key = :key AND domain = :domain AND active = true AND tenant_id = :tid"
            ), {"key": key, "domain": domain, "tid": tenant_id})
            db.commit()
            return bool(getattr(result, "rowcount", 0))
        except Exception:  # noqa: BLE001 — Knowledge-Store-Abfrage fehlgeschlagen; Standardwert wird zurückgegeben
            pass

    store_key = _store_key(tenant_id, domain, key)
    if store_key in _IN_MEMORY_STORE:
        del _IN_MEMORY_STORE[store_key]
        return True
    return False


def get_knowledge_stats(
    db: Optional[Session],
    tenant_id: str = "system",
) -> dict:
    if db:
        try:
            rows = db.execute(text(
                "SELECT knowledge_type, COUNT(*) FROM domain_shared.knowledge_store "
                "WHERE active = true AND tenant_id = :tid GROUP BY knowledge_type"
            ), {"tid": tenant_id}).fetchall()
            return {row[0]: row[1] for row in rows}
        except Exception:  # noqa: BLE001 — Knowledge-Store-Abfrage fehlgeschlagen; Standardwert wird zurückgegeben
            pass

    stats: dict[str, int] = {}
    for key, entry in _IN_MEMORY_STORE.items():
        if not key.startswith(f"{tenant_id}:"):
            continue
        kt = entry.knowledge_type.value
        stats[kt] = stats.get(kt, 0) + 1
    return stats
