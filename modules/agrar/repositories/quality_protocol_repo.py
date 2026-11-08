"""
Quality Protocol Repository - SQLAlchemy Implementation.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.infrastructure.models import HarvestAcceptance, QualityProtocol
from modules.agrar.services.quality_protocol_service import (
    QualityProtocol as ServiceQualityProtocol,
    QualityProtocolRepository,
    QualityProtocolUpdate,
)


class AcceptanceNotOwnedError(ValueError):
    """The referenced acceptance does not exist in the active tenant."""


class QualityProtocolRepositoryImpl:
    """SQLAlchemy-Implementierung des Quality Protocol Repository."""
    
    def __init__(self, db: Session, tenant_id: str):
        if not tenant_id:
            raise ValueError("Tenant context required for quality protocols")
        self.db = db
        self.tenant_id = tenant_id

    def ensure_acceptance_owned(self, acceptance_id: str | None, *, lock: bool = False) -> None:
        if acceptance_id is None:
            return
        query = self.db.query(HarvestAcceptance).filter(
            HarvestAcceptance.id == acceptance_id,
            HarvestAcceptance.tenant_id == self.tenant_id,
        )
        # Serializes version allocation for one acceptance; ordinary reads stay nonblocking.
        if lock:
            query = query.with_for_update().populate_existing()
        parent = query.first()
        if parent is None:
            raise AcceptanceNotOwnedError("Harvest acceptance not found for tenant")
    
    def _to_service(self, db_model: QualityProtocol) -> ServiceQualityProtocol:
        """Konvertiert DB-Model zu Service-Model."""
        return ServiceQualityProtocol(
            id=db_model.id,
            tenant_id=db_model.tenant_id,
            harvest_acceptance_id=db_model.harvest_acceptance_id,
            protocol_number=db_model.protocol_number,
            version=db_model.version,
            moisture_pct=db_model.moisture_pct,
            impurities_pct=db_model.impurities_pct,
            hl_weight_kg_per_hl=db_model.hl_weight_kg_per_hl,
            protein_pct=db_model.protein_pct,
            mycotoxin_ppb=db_model.mycotoxin_ppb,
            other_values=db_model.other_values,
            source_type=db_model.source_type,
            source_device_id=db_model.source_device_id,
            source_file_name=db_model.source_file_name,
            source_file_content=db_model.source_file_content,
            is_final=db_model.is_final,
            approved_by=db_model.approved_by,
            approved_at=db_model.approved_at,
            created_at=db_model.created_at,
            created_by=db_model.created_by,
            updated_at=db_model.updated_at,
            updated_by=db_model.updated_by,
        )
    
    def _from_service(self, service_model: ServiceQualityProtocol) -> QualityProtocol:
        """Konvertiert Service-Model zu DB-Model."""
        return QualityProtocol(
            id=service_model.id,
            tenant_id=service_model.tenant_id,
            harvest_acceptance_id=service_model.harvest_acceptance_id,
            protocol_number=service_model.protocol_number,
            version=service_model.version,
            moisture_pct=service_model.moisture_pct,
            impurities_pct=service_model.impurities_pct,
            hl_weight_kg_per_hl=service_model.hl_weight_kg_per_hl,
            protein_pct=service_model.protein_pct,
            mycotoxin_ppb=service_model.mycotoxin_ppb,
            other_values=service_model.other_values,
            source_type=service_model.source_type,
            source_device_id=service_model.source_device_id,
            source_file_name=service_model.source_file_name,
            source_file_content=service_model.source_file_content,
            is_final=service_model.is_final,
            approved_by=service_model.approved_by,
            approved_at=service_model.approved_at,
            created_at=service_model.created_at,
            created_by=service_model.created_by,
            updated_at=service_model.updated_at,
            updated_by=service_model.updated_by,
        )
    
    def create(self, protocol: ServiceQualityProtocol) -> ServiceQualityProtocol:
        """Erstellt ein neues Qualitätsprotokoll."""
        if protocol.tenant_id != self.tenant_id:
            raise ValueError("Quality protocol tenant mismatch")
        self.ensure_acceptance_owned(protocol.harvest_acceptance_id)
        db_model = self._from_service(protocol)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service(db_model)
    
    def get_by_id(self, protocol_id: str) -> Optional[ServiceQualityProtocol]:
        """Ruft ein Protokoll anhand der ID ab."""
        db_model = self.db.query(QualityProtocol).filter(
            QualityProtocol.id == protocol_id,
            QualityProtocol.tenant_id == self.tenant_id,
        ).first()
        
        if not db_model:
            return None
        
        return self._to_service(db_model)
    
    def get_by_harvest_acceptance(self, harvest_acceptance_id: str) -> list[ServiceQualityProtocol]:
        """Ruft alle Protokolle für eine Ernte-Annahme ab."""
        self.ensure_acceptance_owned(harvest_acceptance_id)
        db_models = self.db.query(QualityProtocol).filter(
            QualityProtocol.harvest_acceptance_id == harvest_acceptance_id,
            QualityProtocol.tenant_id == self.tenant_id,
        ).order_by(QualityProtocol.version.asc()).all()
        
        return [self._to_service(m) for m in db_models]
    
    def get_latest(self, harvest_acceptance_id: str) -> Optional[ServiceQualityProtocol]:
        """Ruft das neueste Protokoll für eine Ernte-Annahme ab."""
        self.ensure_acceptance_owned(harvest_acceptance_id)
        db_model = self.db.query(QualityProtocol).filter(
            QualityProtocol.harvest_acceptance_id == harvest_acceptance_id,
            QualityProtocol.tenant_id == self.tenant_id,
        ).order_by(desc(QualityProtocol.version)).first()
        
        if not db_model:
            return None
        
        return self._to_service(db_model)
    
    def update(self, protocol_id: str, update: QualityProtocolUpdate) -> ServiceQualityProtocol:
        """Aktualisiert ein Protokoll."""
        db_model = self.db.query(QualityProtocol).filter(
            QualityProtocol.id == protocol_id,
            QualityProtocol.tenant_id == self.tenant_id,
        ).with_for_update().populate_existing().first()
        
        if not db_model:
            raise ValueError(f"Quality protocol {protocol_id} not found")
        if db_model.is_final:
            raise ValueError(f"Quality protocol {protocol_id} is finalized and cannot be updated")
        
        # Update Felder
        if update.moisture_pct is not None:
            db_model.moisture_pct = update.moisture_pct
        if update.impurities_pct is not None:
            db_model.impurities_pct = update.impurities_pct
        if update.hl_weight_kg_per_hl is not None:
            db_model.hl_weight_kg_per_hl = update.hl_weight_kg_per_hl
        if update.protein_pct is not None:
            db_model.protein_pct = update.protein_pct
        if update.mycotoxin_ppb is not None:
            db_model.mycotoxin_ppb = update.mycotoxin_ppb
        if update.other_values is not None:
            db_model.other_values = update.other_values
        
        db_model.updated_at = datetime.now()
        db_model.updated_by = update.updated_by
        
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service(db_model)
    
    def finalize(self, protocol_id: str, approved_by: str) -> ServiceQualityProtocol:
        """Finalisiert ein Protokoll."""
        db_model = self.db.query(QualityProtocol).filter(
            QualityProtocol.id == protocol_id,
            QualityProtocol.tenant_id == self.tenant_id,
        ).with_for_update().populate_existing().first()
        
        if not db_model:
            raise ValueError(f"Quality protocol {protocol_id} not found")
        if db_model.is_final:
            raise ValueError(f"Quality protocol {protocol_id} is already finalized")
        
        db_model.is_final = True
        db_model.approved_by = approved_by
        db_model.approved_at = datetime.now()
        db_model.updated_at = datetime.now()
        
        # The API inserts the completion outbox event before committing this transaction.
        self.db.flush()
        self.db.refresh(db_model)
        return self._to_service(db_model)


