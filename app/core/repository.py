"""Generic SQLAlchemy repository with tenant-scoped CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError, TenantMismatchError

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """CRUD base for all tenant-scoped SQLAlchemy models.

    Subclasses only need to declare ``model``:
        class AccountRepository(BaseRepository[Account]):
            model = Account
    """

    model: Type[T]

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── internal helpers ──────────────────────────────────────────────────────

    def _base_query(self):
        return self.db.query(self.model).filter(
            self.model.tenant_id == self.tenant_id  # type: ignore[attr-defined]
        )

    # ── read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, id: str) -> T:
        obj = self._base_query().filter(self.model.id == id).first()  # type: ignore[attr-defined]
        if obj is None:
            raise EntityNotFoundError(self.model.__name__, id)
        return obj

    def get_by_id_or_none(self, id: str) -> Optional[T]:
        return self._base_query().filter(self.model.id == id).first()  # type: ignore[attr-defined]

    def list_paginated(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[List[Any]] = None,
    ) -> tuple[List[T], int]:
        q = self._base_query()
        if filters:
            q = q.filter(*filters)
        total: int = q.count()
        items: List[T] = q.offset(skip).limit(limit).all()
        return items, total

    # ── write ─────────────────────────────────────────────────────────────────

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: str) -> None:
        obj = self.get_by_id(id)
        # Ensure the record actually belongs to this tenant before deleting
        if getattr(obj, "tenant_id", None) != self.tenant_id:
            raise TenantMismatchError(self.model.__name__, id)
        self.db.delete(obj)
        self.db.commit()
