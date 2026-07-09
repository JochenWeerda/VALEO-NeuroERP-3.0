from __future__ import annotations

from sqlalchemy.orm import Session

from app.infrastructure.models import Article, BusinessPartner


class PartyLookupAdapter:
    """Adapter for customer/supplier master-data lookups."""

    def __init__(self, db: Session):
        self.db = db

    def get_name(self, party_id: str) -> str:
        return (
            self.db.query(BusinessPartner.name_1)
            .filter(BusinessPartner.partner_id == party_id)
            .scalar()
            or party_id
        )


class ArticleLookupAdapter:
    """Adapter for article master-data lookups."""

    def __init__(self, db: Session):
        self.db = db

    def get_label(self, article_id: str, fallback: str | None = None) -> str:
        return (
            self.db.query(Article.name)
            .filter(Article.id == article_id)
            .scalar()
            or fallback
            or article_id
        )
