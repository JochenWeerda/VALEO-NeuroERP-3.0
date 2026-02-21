"""add_harvest_acceptance_vat_modes_20260217

Revision ID: add_vat_modes_20260217
Revises: 09e3b0da2b08
Create Date: 2026-02-17 20:00:00.000000

Erweiterte VAT/Steuer-Modi für Ernte-Annahme:
- acceptance_mode: STORAGE_ONLY / PURCHASE_AT_DELIVERY_PTBF / ADVANCE_ON_STORAGE
- ownership_type: THIRD_PARTY_STOCK / OWN_STOCK
- vat_event: NO_INVOICE / PROVISIONAL_CREDIT_NOTE_CREATED / FINAL_CREDIT_NOTE_CREATED / CORRECTION_ISSUED
- §24-Pauschalierung Support (7,8% seit 01.01.2025)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_vat_modes_20260217'
down_revision: Union[str, None] = '09e3b0da2b08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Erweiterte VAT/Steuer-Modi für Harvest Acceptance ────────────────────────────
    
    # acceptance_mode: Geschäftsmodell (STORAGE_ONLY, PURCHASE_AT_DELIVERY_PTBF, ADVANCE_ON_STORAGE)
    op.add_column(
        "harvest_acceptances",
        sa.Column(
            "acceptance_mode",
            sa.String(length=30),
            nullable=True,
            server_default="PURCHASE_AT_DELIVERY_PTBF",
            comment="Geschäftsmodell: STORAGE_ONLY (Fremdware, keine Vorsteuer) / PURCHASE_AT_DELIVERY_PTBF (Ankauf jetzt, Preis später, Vorsteuer möglich) / ADVANCE_ON_STORAGE (Einlagerung + Abschlag/Anzahlung)"
        ),
        schema="domain_inventory",
    )
    
    # ownership_type: Eigentumsverhältnis (THIRD_PARTY_STOCK vs OWN_STOCK)
    op.add_column(
        "harvest_acceptances",
        sa.Column(
            "ownership_type",
            sa.String(length=20),
            nullable=True,
            server_default="OWN_STOCK",
            comment="Eigentumsverhältnis: THIRD_PARTY_STOCK (Fremdware) / OWN_STOCK (Eigene Ware)"
        ),
        schema="domain_inventory",
    )
    
    # vat_event: VAT-Ereignis (NO_INVOICE, PROVISIONAL_CREDIT_NOTE_CREATED, FINAL_CREDIT_NOTE_CREATED, CORRECTION_ISSUED)
    op.add_column(
        "harvest_acceptances",
        sa.Column(
            "vat_event",
            sa.String(length=40),
            nullable=True,
            server_default="NO_INVOICE",
            comment="VAT-Ereignis: NO_INVOICE (Storage) / PROVISIONAL_CREDIT_NOTE_CREATED / FINAL_CREDIT_NOTE_CREATED / CORRECTION_ISSUED"
        ),
        schema="domain_inventory",
    )
    
    # advance_payment_amount_eur: Anzahlungsbetrag (für ADVANCE_ON_STORAGE)
    op.add_column(
        "harvest_acceptances",
        sa.Column(
            "advance_payment_amount_eur",
            sa.DECIMAL(14, 2),
            nullable=True,
            comment="Anzahlungsbetrag (EUR) - für ADVANCE_ON_STORAGE Modus"
        ),
        schema="domain_inventory",
    )
    
    # advance_payment_date: Anzahlungsdatum
    op.add_column(
        "harvest_acceptances",
        sa.Column(
            "advance_payment_date",
            sa.Date(),
            nullable=True,
            comment="Anzahlungsdatum - für ADVANCE_ON_STORAGE Modus"
        ),
        schema="domain_inventory",
    )
    
    # advance_invoice_id: Referenz auf Anzahlungsrechnung/-gutschrift
    op.add_column(
        "harvest_acceptances",
        sa.Column(
            "advance_invoice_id",
            sa.String(),
            sa.ForeignKey("domain_finance.self_billing_invoices.id", ondelete="SET NULL"),
            nullable=True,
            comment="Referenz auf Anzahlungsrechnung/-gutschrift"
        ),
        schema="domain_inventory",
    )
    
    # Erweiterte Indizes
    op.create_index(
        "ix_harvest_acceptances_acceptance_mode",
        "harvest_acceptances",
        ["acceptance_mode"],
        unique=False,
        schema="domain_inventory",
    )
    
    op.create_index(
        "ix_harvest_acceptances_vat_event",
        "harvest_acceptances",
        ["vat_event"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_harvest_acceptances_vat_event", table_name="harvest_acceptances", schema="domain_inventory")
    op.drop_index("ix_harvest_acceptances_acceptance_mode", table_name="harvest_acceptances", schema="domain_inventory")
    
    op.drop_column("harvest_acceptances", "advance_invoice_id", schema="domain_inventory")
    op.drop_column("harvest_acceptances", "advance_payment_date", schema="domain_inventory")
    op.drop_column("harvest_acceptances", "advance_payment_amount_eur", schema="domain_inventory")
    op.drop_column("harvest_acceptances", "vat_event", schema="domain_inventory")
    op.drop_column("harvest_acceptances", "ownership_type", schema="domain_inventory")
    op.drop_column("harvest_acceptances", "acceptance_mode", schema="domain_inventory")


