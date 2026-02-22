"""
Daily Price Repository - SQLAlchemy Implementation.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.infrastructure.models import DailyPrice
from modules.agrar.services.daily_price_service import (
    DailyPrice as ServiceDailyPrice,
    DailyPriceRepository,
    DailyPriceFilter,
)


class DailyPriceRepositoryImpl:
    """SQLAlchemy-Implementierung des Daily Price Repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_service(self, db_model: DailyPrice) -> ServiceDailyPrice:
        """Konvertiert DB-Model zu Service-Model."""
        return ServiceDailyPrice(
            id=db_model.id,
            tenant_id=db_model.tenant_id,
            article_id=db_model.article_id,
            warengruppe=db_model.warengruppe,
            crop_code=db_model.crop_code,
            price_eur_per_ton=db_model.price_eur_per_ton,
            currency=db_model.currency,
            price_date=db_model.price_date,
            valid_from=db_model.valid_from,
            valid_to=db_model.valid_to,
            source_type=db_model.source_type,
            source_id=db_model.source_id,
            source_name=db_model.source_name,
            created_at=db_model.created_at,
            created_by=db_model.created_by,
            updated_at=db_model.updated_at,
            updated_by=db_model.updated_by,
        )
    
    def _from_service(self, service_model: ServiceDailyPrice) -> DailyPrice:
        """Konvertiert Service-Model zu DB-Model."""
        return DailyPrice(
            id=service_model.id,
            tenant_id=service_model.tenant_id,
            article_id=service_model.article_id,
            warengruppe=service_model.warengruppe,
            crop_code=service_model.crop_code,
            price_eur_per_ton=service_model.price_eur_per_ton,
            currency=service_model.currency,
            price_date=service_model.price_date,
            valid_from=service_model.valid_from,
            valid_to=service_model.valid_to,
            source_type=service_model.source_type,
            source_id=service_model.source_id,
            source_name=service_model.source_name,
            created_at=service_model.created_at,
            created_by=service_model.created_by,
            updated_at=service_model.updated_at,
            updated_by=service_model.updated_by,
        )
    
    def create(self, price: ServiceDailyPrice) -> ServiceDailyPrice:
        """Erstellt einen neuen Tagespreis."""
        db_model = self._from_service(price)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service(db_model)
    
    def get_by_id(self, price_id: str) -> Optional[ServiceDailyPrice]:
        """Ruft einen Preis anhand der ID ab."""
        db_model = self.db.query(DailyPrice).filter(
            DailyPrice.id == price_id
        ).first()
        
        if not db_model:
            return None
        
        return self._to_service(db_model)
    
    def find_price(self, filter: DailyPriceFilter) -> Optional[ServiceDailyPrice]:
        """
        Findet einen Preis basierend auf Filterkriterien.
        
        Priorität:
        1. article_id (falls vorhanden)
        2. warengruppe (falls vorhanden)
        3. crop_code (falls vorhanden)
        """
        query = self.db.query(DailyPrice).filter(
            DailyPrice.tenant_id == filter.tenant_id
        )
        
        # Gültigkeitsprüfung
        valid_at = filter.valid_at or datetime.now()
        query = query.filter(
            DailyPrice.valid_from <= valid_at
        ).filter(
            or_(
                DailyPrice.valid_to.is_(None),
                DailyPrice.valid_to >= valid_at
            )
        )
        
        # Preis-Datum
        if filter.price_date:
            query = query.filter(DailyPrice.price_date == filter.price_date)
        
        # Priorität: article_id > warengruppe > crop_code
        if filter.article_id:
            query = query.filter(DailyPrice.article_id == filter.article_id)
        elif filter.warengruppe:
            query = query.filter(DailyPrice.warengruppe == filter.warengruppe)
        elif filter.crop_code:
            query = query.filter(DailyPrice.crop_code == filter.crop_code)
        else:
            return None
        
        # Neuesten Preis nehmen (falls mehrere)
        db_model = query.order_by(desc(DailyPrice.price_date)).first()
        
        if not db_model:
            return None
        
        return self._to_service(db_model)
    
    def get_price_history(
        self,
        tenant_id: str,
        article_id: Optional[str] = None,
        warengruppe: Optional[str] = None,
        crop_code: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 100,
    ) -> list[ServiceDailyPrice]:
        """Ruft Preis-Historie ab."""
        query = self.db.query(DailyPrice).filter(
            DailyPrice.tenant_id == tenant_id
        )
        
        if article_id:
            query = query.filter(DailyPrice.article_id == article_id)
        if warengruppe:
            query = query.filter(DailyPrice.warengruppe == warengruppe)
        if crop_code:
            query = query.filter(DailyPrice.crop_code == crop_code)
        if from_date:
            query = query.filter(DailyPrice.price_date >= from_date)
        if to_date:
            query = query.filter(DailyPrice.price_date <= to_date)
        
        db_models = query.order_by(desc(DailyPrice.price_date)).limit(limit).all()
        
        return [self._to_service(m) for m in db_models]
    
    def bulk_create(self, prices: list[ServiceDailyPrice]) -> list[ServiceDailyPrice]:
        """Erstellt mehrere Preise auf einmal."""
        db_models = [self._from_service(p) for p in prices]
        self.db.add_all(db_models)
        self.db.commit()
        
        # Refresh alle Models
        for db_model in db_models:
            self.db.refresh(db_model)
        
        return [self._to_service(m) for m in db_models]


