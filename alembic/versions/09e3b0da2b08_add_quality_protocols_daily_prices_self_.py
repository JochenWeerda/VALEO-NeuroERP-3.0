"""add_quality_protocols_daily_prices_self_billing_dispute_nuts2_20260217

Revision ID: 09e3b0da2b08
Revises: c4d5e6f7a8b9
Create Date: 2026-02-18 13:31:22.282179

Erweiterte Features für Ernte-Annahme:
- quality_protocols: Qualitätsprotokolle für Laborwerte
- daily_prices: Tagespreise für dynamische Preisermittlung
- self_billing_invoices: Self-Billing Gutschriften
- dispute_records: Dispute-Handling
- nuts2_postal_codes: NUTS-2 Zuordnungstabelle
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '09e3b0da2b08'
down_revision: Union[str, None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Qualitätsprotokolle ────────────────────────────────────────────────────────
    
    op.create_table(
        "quality_protocols",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("domain_shared.tenants.id"), nullable=False),
        sa.Column("harvest_acceptance_id", sa.String(), sa.ForeignKey("domain_inventory.harvest_acceptances.id", ondelete="SET NULL"), nullable=True),
        sa.Column("protocol_number", sa.String(length=50), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        
        # Laborwerte
        sa.Column("moisture_pct", sa.DECIMAL(5, 2), nullable=True, comment="Feuchte (%)"),
        sa.Column("impurities_pct", sa.DECIMAL(5, 2), nullable=True, comment="Besatz (%)"),
        sa.Column("hl_weight_kg_per_hl", sa.DECIMAL(6, 2), nullable=True, comment="Hektolitergewicht (kg/hl)"),
        sa.Column("protein_pct", sa.DECIMAL(5, 2), nullable=True, comment="Protein (%)"),
        sa.Column("mycotoxin_ppb", sa.DECIMAL(10, 2), nullable=True, comment="Mykotoxin (ppb)"),
        sa.Column("other_values", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Weitere Laborwerte (JSONB)"),
        
        # Quelle
        sa.Column("source_type", sa.String(length=20), nullable=True, comment="Quelle: manual / import / lims / device"),
        sa.Column("source_device_id", sa.String(length=64), nullable=True),
        sa.Column("source_file_name", sa.String(length=255), nullable=True),
        sa.Column("source_file_content", sa.Text(), nullable=True, comment="Original-Dateiinhalt (für Audit)"),
        
        # Status
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("approved_by", sa.String(length=64), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        
        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        schema="domain_inventory",
    )
    op.create_primary_key("pk_quality_protocols", "quality_protocols", ["id"], schema="domain_inventory")
    op.create_index("ix_quality_protocols_harvest_acceptance_id", "quality_protocols", ["harvest_acceptance_id"], schema="domain_inventory")
    op.create_index("ix_quality_protocols_protocol_number", "quality_protocols", ["protocol_number", "version"], schema="domain_inventory")
    op.create_index("ix_quality_protocols_tenant_id", "quality_protocols", ["tenant_id"], schema="domain_inventory")
    
    # ── Tagespreise ────────────────────────────────────────────────────────────────
    
    op.create_table(
        "daily_prices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("domain_shared.tenants.id"), nullable=False),
        sa.Column("article_id", sa.String(), sa.ForeignKey("domain_inventory.articles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("warengruppe", sa.String(length=80), nullable=True, comment="Warengruppe (falls artikel_id NULL)"),
        sa.Column("crop_code", sa.String(length=20), nullable=True, comment="Crop Code (MAIZE, WHEAT, BARLEY, etc.)"),
        
        # Preis
        sa.Column("price_eur_per_ton", sa.DECIMAL(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        
        # Gültigkeit
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        
        # Quelle
        sa.Column("source_type", sa.String(length=20), nullable=True, comment="Quelle: manual / exchange / api"),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        
        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        schema="domain_inventory",
    )
    op.create_primary_key("pk_daily_prices", "daily_prices", ["id"], schema="domain_inventory")
    op.create_index("ix_daily_prices_article_id", "daily_prices", ["article_id", "price_date"], schema="domain_inventory")
    op.create_index("ix_daily_prices_warengruppe", "daily_prices", ["warengruppe", "price_date"], schema="domain_inventory")
    op.create_index("ix_daily_prices_crop_code", "daily_prices", ["crop_code", "price_date"], schema="domain_inventory")
    op.create_index("ix_daily_prices_price_date", "daily_prices", ["price_date"], schema="domain_inventory")
    op.create_index("ix_daily_prices_tenant_id", "daily_prices", ["tenant_id"], schema="domain_inventory")
    
    # ── Self-Billing Invoices ───────────────────────────────────────────────────────
    
    # Prüfen, ob domain_finance Schema existiert, sonst erstellen
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_finance")
    
    op.create_table(
        "self_billing_invoices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("domain_shared.tenants.id"), nullable=False),
        sa.Column("harvest_acceptance_id", sa.String(), sa.ForeignKey("domain_inventory.harvest_acceptances.id", ondelete="SET NULL"), nullable=True),
        
        # Rechnungsnummern
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("provisional_invoice_number", sa.String(length=50), nullable=True),
        
        # Status
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft", comment="draft / issued / paid / disputed / cancelled"),
        sa.Column("dispute_status", sa.String(length=20), nullable=True, comment="none / raised / resolved / rejected"),
        sa.Column("dispute_reason", sa.Text(), nullable=True),
        sa.Column("dispute_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dispute_user_id", sa.String(length=64), nullable=True),
        
        # Beträge
        sa.Column("total_net_amount_eur", sa.DECIMAL(15, 2), nullable=False),
        sa.Column("total_vat_amount_eur", sa.DECIMAL(15, 2), nullable=False),
        sa.Column("total_gross_amount_eur", sa.DECIMAL(15, 2), nullable=False),
        sa.Column("vat_rate_percent", sa.DECIMAL(5, 2), nullable=False),
        
        # E-Rechnung
        sa.Column("einvoice_xml", sa.Text(), nullable=True, comment="XRechnung/ZUGFeRD XML"),
        sa.Column("einvoice_pdf", postgresql.BYTEA(), nullable=True, comment="PDF (optional)"),
        sa.Column("einvoice_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("einvoice_received_at", sa.DateTime(timezone=True), nullable=True),
        
        # Pflichttexte
        sa.Column("mandatory_texts", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Array von Pflichttexten (JSONB)"),
        
        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        schema="domain_finance",
    )
    op.create_primary_key("pk_self_billing_invoices", "self_billing_invoices", ["id"], schema="domain_finance")
    op.create_unique_constraint("uq_self_billing_invoices_invoice_number", "self_billing_invoices", ["invoice_number"], schema="domain_finance")
    op.create_index("ix_self_billing_invoices_harvest_acceptance_id", "self_billing_invoices", ["harvest_acceptance_id"], schema="domain_finance")
    op.create_index("ix_self_billing_invoices_status", "self_billing_invoices", ["status"], schema="domain_finance")
    op.create_index("ix_self_billing_invoices_tenant_id", "self_billing_invoices", ["tenant_id"], schema="domain_finance")
    
    # ── Dispute Records ────────────────────────────────────────────────────────────
    
    op.create_table(
        "dispute_records",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("domain_shared.tenants.id"), nullable=False),
        sa.Column("invoice_id", sa.String(), sa.ForeignKey("domain_finance.self_billing_invoices.id", ondelete="CASCADE"), nullable=False),
        
        # Dispute-Details
        sa.Column("dispute_type", sa.String(length=30), nullable=True, comment="amount / quality / quantity / other"),
        sa.Column("dispute_reason", sa.Text(), nullable=False),
        sa.Column("disputed_amount_eur", sa.DECIMAL(15, 2), nullable=True),
        
        # Status
        sa.Column("status", sa.String(length=20), nullable=False, server_default="raised", comment="raised / resolved / rejected"),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("resolved_by", sa.String(length=64), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        
        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        schema="domain_finance",
    )
    op.create_primary_key("pk_dispute_records", "dispute_records", ["id"], schema="domain_finance")
    op.create_index("ix_dispute_records_invoice_id", "dispute_records", ["invoice_id"], schema="domain_finance")
    op.create_index("ix_dispute_records_status", "dispute_records", ["status"], schema="domain_finance")
    op.create_index("ix_dispute_records_tenant_id", "dispute_records", ["tenant_id"], schema="domain_finance")
    
    # ── NUTS-2 Postal Code Correspondence ──────────────────────────────────────────
    
    op.create_table(
        "nuts2_postal_codes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("postal_code", sa.String(length=10), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False, server_default="DE"),
        sa.Column("nuts2_code", sa.String(length=10), nullable=False),
        sa.Column("nuts_version", sa.String(length=20), nullable=False, server_default="NUTS 2024"),
        
        # Gültigkeit
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        
        # Audit
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema="domain_shared",
    )
    op.create_primary_key("pk_nuts2_postal_codes", "nuts2_postal_codes", ["id"], schema="domain_shared")
    op.create_index("ix_nuts2_postal_codes_postal_code", "nuts2_postal_codes", ["postal_code", "country_code"], schema="domain_shared")
    op.create_index("ix_nuts2_postal_codes_nuts2_code", "nuts2_postal_codes", ["nuts2_code"], schema="domain_shared")
    op.create_unique_constraint("uq_nuts2_postal_codes", "nuts2_postal_codes", ["postal_code", "country_code", "valid_from"], schema="domain_shared")


def downgrade() -> None:
    # Tabellen in umgekehrter Reihenfolge löschen
    op.drop_table("nuts2_postal_codes", schema="domain_shared")
    op.drop_table("dispute_records", schema="domain_finance")
    op.drop_table("self_billing_invoices", schema="domain_finance")
    op.drop_table("daily_prices", schema="domain_inventory")
    op.drop_table("quality_protocols", schema="domain_inventory")
