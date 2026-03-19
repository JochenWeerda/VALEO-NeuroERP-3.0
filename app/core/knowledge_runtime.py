"""
Runtime helpers for DB-backed knowledge access with explicit dev/test fallback.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.knowledge_core_contracts import (
    KnowledgeObject,
    KnowledgeRetrievalRequest,
    build_context_pack,
    build_onboarding_bundle,
    get_default_knowledge_objects,
    retrieve_knowledge_objects,
)
from app.repositories.knowledge_repository import KnowledgeRepository


def allow_default_knowledge_fallback() -> bool:
    app_env = (settings.APP_ENV or "").strip().lower()
    return settings.DEBUG or app_env in {"development", "dev", "test", "testing"}


def load_runtime_knowledge_objects(db: Session) -> list[KnowledgeObject]:
    repo = KnowledgeRepository(db)
    if repo.count_objects() > 0:
        return repo.list_domain_objects()
    if allow_default_knowledge_fallback():
        return get_default_knowledge_objects()
    return []


def load_runtime_knowledge_object(db: Session, knowledge_id: str) -> KnowledgeObject | None:
    for obj in load_runtime_knowledge_objects(db):
        if obj.knowledge_id == knowledge_id:
            return obj
    return None


def retrieve_runtime_knowledge(db: Session, request: KnowledgeRetrievalRequest) -> list[dict]:
    objects = load_runtime_knowledge_objects(db)
    if not objects:
        return []
    return retrieve_knowledge_objects(request, objects=objects)


def build_runtime_onboarding_bundle(
    *,
    db: Session,
    rolle: str,
    tenant_id: str | None = None,
    limit: int = 5,
) -> dict:
    objects = load_runtime_knowledge_objects(db)
    return build_onboarding_bundle(
        rolle=rolle,
        tenant_id=tenant_id,
        limit=limit,
        objects=objects or None,
    )


def build_runtime_context_pack(
    *,
    db: Session,
    rolle: str,
    kanal,
    tenant_id: str | None = None,
    capability_key: str | None = None,
    query: str = "",
    limit: int = 4,
):
    objects = load_runtime_knowledge_objects(db)
    return build_context_pack(
        rolle=rolle,
        kanal=kanal,
        tenant_id=tenant_id,
        capability_key=capability_key,
        query=query,
        limit=limit,
        objects=objects or None,
    )
