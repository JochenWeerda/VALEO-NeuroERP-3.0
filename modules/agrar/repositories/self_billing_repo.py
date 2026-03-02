"""
Self-Billing Repository - SQLAlchemy Implementation.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.models import SelfBillingInvoice, DisputeRecord
from modules.agrar.services.self_billing_service import (
    SelfBillingInvoice as ServiceSelfBillingInvoice,
    SelfBillingRepository,
    DisputeRecord as ServiceDisputeRecord,
)


class SelfBillingRepositoryImpl:
    """SQLAlchemy-Implementierung des Self-Billing Repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_service_invoice(self, db_model: SelfBillingInvoice) -> ServiceSelfBillingInvoice:
        """Konvertiert DB-Model zu Service-Model."""
        return ServiceSelfBillingInvoice(
            id=db_model.id,
            tenant_id=db_model.tenant_id,
            harvest_acceptance_id=db_model.harvest_acceptance_id,
            invoice_number=db_model.invoice_number,
            provisional_invoice_number=db_model.provisional_invoice_number,
            status=db_model.status,
            dispute_status=db_model.dispute_status or "none",
            dispute_reason=db_model.dispute_reason,
            dispute_date=db_model.dispute_date,
            dispute_user_id=db_model.dispute_user_id,
            total_net_amount_eur=db_model.total_net_amount_eur,
            total_vat_amount_eur=db_model.total_vat_amount_eur,
            total_gross_amount_eur=db_model.total_gross_amount_eur,
            vat_rate_percent=db_model.vat_rate_percent,
            einvoice_xml=db_model.einvoice_xml,
            einvoice_pdf=db_model.einvoice_pdf,
            einvoice_sent_at=db_model.einvoice_sent_at,
            einvoice_received_at=db_model.einvoice_received_at,
            mandatory_texts=db_model.mandatory_texts,
            created_at=db_model.created_at,
            created_by=db_model.created_by,
            updated_at=db_model.updated_at,
            updated_by=db_model.updated_by,
        )
    
    def _from_service_invoice(self, service_model: ServiceSelfBillingInvoice) -> SelfBillingInvoice:
        """Konvertiert Service-Model zu DB-Model."""
        return SelfBillingInvoice(
            id=service_model.id,
            tenant_id=service_model.tenant_id,
            harvest_acceptance_id=service_model.harvest_acceptance_id,
            invoice_number=service_model.invoice_number,
            provisional_invoice_number=service_model.provisional_invoice_number,
            status=service_model.status,
            dispute_status=service_model.dispute_status if service_model.dispute_status != "none" else None,
            dispute_reason=service_model.dispute_reason,
            dispute_date=service_model.dispute_date,
            dispute_user_id=service_model.dispute_user_id,
            total_net_amount_eur=service_model.total_net_amount_eur,
            total_vat_amount_eur=service_model.total_vat_amount_eur,
            total_gross_amount_eur=service_model.total_gross_amount_eur,
            vat_rate_percent=service_model.vat_rate_percent,
            einvoice_xml=service_model.einvoice_xml,
            einvoice_pdf=service_model.einvoice_pdf,
            einvoice_sent_at=service_model.einvoice_sent_at,
            einvoice_received_at=service_model.einvoice_received_at,
            mandatory_texts=service_model.mandatory_texts,
            created_at=service_model.created_at,
            created_by=service_model.created_by,
            updated_at=service_model.updated_at,
            updated_by=service_model.updated_by,
        )
    
    def _to_service_dispute(self, db_model: DisputeRecord) -> ServiceDisputeRecord:
        """Konvertiert DB-Model zu Service-Model."""
        return ServiceDisputeRecord(
            id=db_model.id,
            tenant_id=db_model.tenant_id,
            invoice_id=db_model.invoice_id,
            dispute_type=db_model.dispute_type,
            dispute_reason=db_model.dispute_reason,
            disputed_amount_eur=db_model.disputed_amount_eur,
            status=db_model.status,
            resolution_notes=db_model.resolution_notes,
            resolved_by=db_model.resolved_by,
            resolved_at=db_model.resolved_at,
            created_at=db_model.created_at,
            created_by=db_model.created_by,
            updated_at=db_model.updated_at,
            updated_by=db_model.updated_by,
        )
    
    def create_invoice(self, invoice: ServiceSelfBillingInvoice) -> ServiceSelfBillingInvoice:
        """Erstellt eine neue Gutschrift."""
        db_model = self._from_service_invoice(invoice)
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service_invoice(db_model)
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[ServiceSelfBillingInvoice]:
        """Ruft eine Gutschrift anhand der ID ab."""
        db_model = self.db.query(SelfBillingInvoice).filter(
            SelfBillingInvoice.id == invoice_id
        ).first()
        
        if not db_model:
            return None
        
        return self._to_service_invoice(db_model)
    
    def get_invoice_by_harvest_acceptance(self, harvest_acceptance_id: str) -> Optional[ServiceSelfBillingInvoice]:
        """Ruft die Gutschrift für eine Ernte-Annahme ab."""
        db_model = self.db.query(SelfBillingInvoice).filter(
            SelfBillingInvoice.harvest_acceptance_id == harvest_acceptance_id
        ).first()
        
        if not db_model:
            return None
        
        return self._to_service_invoice(db_model)
    
    def update_invoice(self, invoice_id: str, updates: dict) -> ServiceSelfBillingInvoice:
        """Aktualisiert eine Gutschrift."""
        db_model = self.db.query(SelfBillingInvoice).filter(
            SelfBillingInvoice.id == invoice_id
        ).first()
        
        if not db_model:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        # Update Felder
        for key, value in updates.items():
            if hasattr(db_model, key) and value is not None:
                setattr(db_model, key, value)
        
        if "updated_at" not in updates:
            db_model.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service_invoice(db_model)
    
    def create_dispute(self, dispute: ServiceDisputeRecord) -> ServiceDisputeRecord:
        """Erstellt einen Dispute-Record."""
        db_model = DisputeRecord(
            id=dispute.id,
            tenant_id=dispute.tenant_id,
            invoice_id=dispute.invoice_id,
            dispute_type=dispute.dispute_type,
            dispute_reason=dispute.dispute_reason,
            disputed_amount_eur=dispute.disputed_amount_eur,
            status=dispute.status,
            resolution_notes=dispute.resolution_notes,
            resolved_by=dispute.resolved_by,
            resolved_at=dispute.resolved_at,
            created_at=dispute.created_at,
            created_by=dispute.created_by,
            updated_at=dispute.updated_at,
            updated_by=dispute.updated_by,
        )
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service_dispute(db_model)
    
    def get_disputes_by_invoice(self, invoice_id: str) -> list[ServiceDisputeRecord]:
        """Ruft alle Disputes für eine Gutschrift ab."""
        db_models = self.db.query(DisputeRecord).filter(
            DisputeRecord.invoice_id == invoice_id
        ).order_by(DisputeRecord.created_at.desc()).all()

        return [self._to_service_dispute(m) for m in db_models]

    def get_dispute_by_id(self, dispute_id: str) -> Optional[ServiceDisputeRecord]:
        """Ruft einen einzelnen Dispute anhand der ID ab."""
        db_model = self.db.query(DisputeRecord).filter(
            DisputeRecord.id == dispute_id
        ).first()
        return self._to_service_dispute(db_model) if db_model else None

    def update_dispute(self, dispute_id: str, updates: dict) -> ServiceDisputeRecord:
        """Aktualisiert einen Dispute-Record."""
        db_model = self.db.query(DisputeRecord).filter(
            DisputeRecord.id == dispute_id
        ).first()
        if not db_model:
            raise ValueError(f"Dispute {dispute_id} not found")
        for k, v in updates.items():
            if hasattr(db_model, k):
                setattr(db_model, k, v)
        if "updated_at" not in updates:
            db_model.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_service_dispute(db_model)


