"""add_harvest_acceptance_extensions_20260217

Revision ID: c4d5e6f7a8b9
Revises: b38680c2f581
Create Date: 2026-02-17 15:30:00.000000

Erweiterungen nach praxisnahen Default-Entscheidungen:
- pricing_mode + price_source_id am HarvestAcceptance
- Erweiterte Status-Workflow (credit_note_created, paid, disputed, cancelled)
- harvest_acceptance_lines für Silo/Partie-Splits
- supplier_tax_profiles für Steuerprofile mit Gültigkeit
- price_adjustment_rules für konfigurierbare Zu-/Abschläge
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, None] = 'b38680c2f581'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Erweiterte Harvest Acceptance Felder ────────────────────────────────────
    
    # pricing_mode + price_source_id
    op.add_column(
        "harvest_acceptances",
        sa.Column("pricing_mode", sa.String(length=20), nullable=False, server_default="spot_daily", comment="Preismodell: fixed_contract / spot_daily / exchange_fix_later"),
        schema="domain_inventory",
    )
    op.add_column(
        "harvest_acceptances",
        sa.Column("price_source_id", sa.String(length=64), nullable=True, comment="Referenz zu Preisquelle (daily_price_id, exchange_index_id, etc.)"),
        schema="domain_inventory",
    )
    
    # Erweiterte Status-Workflow (Kommentar aktualisieren)
    op.alter_column(
        "harvest_acceptances",
        "release_status",
        existing_type=sa.String(length=20),
        comment="Freigabe: draft / provisional / final / credit_note_created / paid / disputed / cancelled",
        schema="domain_inventory",
    )
    
    # ── Harvest Acceptance Lines (für Silo/Partie-Splits) ───────────────────────
    op.create_table(
        "harvest_acceptance_lines",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("harvest_acceptance_id", sa.String(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False, comment="Zeilennummer (1, 2, 3, ...)"),
        sa.Column("silo_id", sa.String(length=64), nullable=True, comment="Silo-Nr./Lagerort"),
        sa.Column("lot_id", sa.String(length=64), nullable=True, comment="Partie/Charge"),
        sa.Column("qty_kg_allocated", sa.DECIMAL(12, 3), nullable=False, comment="Zugeordnete Menge (kg)"),
        sa.Column("notes", sa.Text(), nullable=True, comment="Bemerkungen zur Verteilung"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["harvest_acceptance_id"], ["domain_inventory.harvest_acceptances.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_harvest_acceptance_lines_acceptance",
        "harvest_acceptance_lines",
        ["harvest_acceptance_id", "line_number"],
        unique=False,
        schema="domain_inventory",
    )
    
    # ── Supplier Tax Profiles ────────────────────────────────────────────────────
    op.create_table(
        "supplier_tax_profiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("supplier_id", sa.String(), nullable=False, comment="Lieferant (Business Partner)"),
        sa.Column("taxation_type", sa.String(length=20), nullable=False, comment="Besteuerungsart: regular / ustg24_flat_rate / small_business"),
        sa.Column("vat_id", sa.String(length=30), nullable=True, comment="USt-ID (optional)"),
        sa.Column("valid_from", sa.Date(), nullable=False, comment="Gültig ab"),
        sa.Column("valid_to", sa.Date(), nullable=True, comment="Gültig bis (NULL = unbegrenzt)"),
        sa.Column("notes", sa.Text(), nullable=True, comment="Hinweise/Texts"),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["supplier_id"], ["domain_crm.business_partners.partner_id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_crm",
    )
    op.create_index(
        "ix_supplier_tax_profiles_supplier_valid",
        "supplier_tax_profiles",
        ["supplier_id", "valid_from", "valid_to"],
        unique=False,
        schema="domain_crm",
    )
    
    # ── Price Adjustment Rules ──────────────────────────────────────────────────
    op.create_table(
        "price_adjustment_rules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("article_id", sa.String(), nullable=True, comment="Artikel (optional, wenn warengruppe-basiert)"),
        sa.Column("warengruppe", sa.String(length=80), nullable=True, comment="Warengruppe (optional, wenn artikel-basiert)"),
        sa.Column("adjustment_type", sa.String(length=30), nullable=False, comment="Typ: hl_weight / impurity / mycotoxin / other"),
        sa.Column("parameter_name", sa.String(length=50), nullable=False, comment="Parameter (z.B. 'hl_weight_kg_per_hl', 'impurity_pct')"),
        sa.Column("method", sa.String(length=20), nullable=False, comment="Methode: table / factor / percentage"),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Staffeln/Tabelle (JSONB)"),
        sa.Column("effective_from", sa.Date(), nullable=False, comment="Gültig ab"),
        sa.Column("effective_to", sa.Date(), nullable=True, comment="Gültig bis (NULL = unbegrenzt)"),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("created_by", sa.String(length=64), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["domain_inventory.articles.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_price_adjustment_rules_article_valid",
        "price_adjustment_rules",
        ["article_id", "warengruppe", "adjustment_type", "effective_from", "effective_to"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_price_adjustment_rules_article_valid", table_name="price_adjustment_rules", schema="domain_inventory")
    op.drop_index("ix_supplier_tax_profiles_supplier_valid", table_name="supplier_tax_profiles", schema="domain_crm")
    op.drop_index("ix_harvest_acceptance_lines_acceptance", table_name="harvest_acceptance_lines", schema="domain_inventory")
    
    # Drop tables
    op.drop_table("price_adjustment_rules", schema="domain_inventory")
    op.drop_table("supplier_tax_profiles", schema="domain_crm")
    op.drop_table("harvest_acceptance_lines", schema="domain_inventory")
    
    # Drop columns
    op.drop_column("harvest_acceptances", "price_source_id", schema="domain_inventory")
    op.drop_column("harvest_acceptances", "pricing_mode", schema="domain_inventory")
    
    # Restore original comment
    op.alter_column(
        "harvest_acceptances",
        "release_status",
        existing_type=sa.String(length=20),
        comment="Freigabe: draft / provisional / final",
        schema="domain_inventory",
    )


