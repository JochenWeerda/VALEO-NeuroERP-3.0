"""DOM-FINANCE-004: finance_sepa_mandate, sepa_batches, ratenzahlungsplaene, ratenzahlungsraten, mahnstufen_audit

Revision ID: finance_sepa_ratenzahlung_20260623
Revises: compliance_pcn_audit_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "finance_sepa_ratenzahlung_20260623"
down_revision = "compliance_pcn_audit_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_finance")

    op.create_table(
        "finance_sepa_mandate",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("mandat_ref", sa.String(60), nullable=False, unique=True),
        sa.Column("glaeubiger_id", sa.String(100), nullable=False),
        sa.Column("iban", sa.String(34), nullable=False),
        sa.Column("bic", sa.String(11)),
        sa.Column("typ", sa.String(10), server_default="CORE"),
        sa.Column("status", sa.String(20), server_default="AKTIV"),
        sa.Column("erteilung_am", sa.Date, nullable=True),
        sa.Column("widerruf_am", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_finance",
    )
    op.create_index("ix_sepa_mandate_tenant", "finance_sepa_mandate", ["tenant_id"], schema="domain_finance")

    op.create_table(
        "finance_sepa_batches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("faellig_am", sa.Date, nullable=False),
        sa.Column("gesamt_eur", sa.Numeric(14, 2)),
        sa.Column("status", sa.String(20), server_default="ERSTELLT"),
        sa.Column("xml_payload", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_finance",
    )
    op.create_index("ix_sepa_batches_tenant", "finance_sepa_batches", ["tenant_id"], schema="domain_finance")

    op.create_table(
        "finance_ratenzahlungsplaene",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("op_id", sa.String(36), nullable=False),
        sa.Column("gesamt_eur", sa.Numeric(14, 2)),
        sa.Column("anzahl_raten", sa.Integer),
        sa.Column("restbetrag_eur", sa.Numeric(14, 2)),
        sa.Column("status", sa.String(20), server_default="AKTIV"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("op_id", "tenant_id", name="uq_ratenzahlungsplan_op"),
        schema="domain_finance",
    )
    op.create_index("ix_ratenzahlungsplaene_tenant", "finance_ratenzahlungsplaene", ["tenant_id"], schema="domain_finance")

    op.create_table(
        "finance_ratenzahlungsraten",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("plan_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("rate_nr", sa.Integer, nullable=False),
        sa.Column("betrag_eur", sa.Numeric(14, 2)),
        sa.Column("faellig_am", sa.Date),
        sa.Column("bezahlt_am", sa.Date, nullable=True),
        sa.Column("status", sa.String(20), server_default="OFFEN"),
        schema="domain_finance",
    )
    op.create_index("ix_ratenzahlungsraten_plan", "finance_ratenzahlungsraten", ["plan_id"], schema="domain_finance")

    op.create_table(
        "finance_mahnstufen_audit",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("rechnungsnr", sa.String(60), nullable=False),
        sa.Column("stufe", sa.String(20), nullable=False),
        sa.Column("operator", sa.String(100)),
        sa.Column("bearbeitungsgebuehr_eur", sa.Numeric(10, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_finance",
    )
    op.create_index(
        "ix_mahnstufen_audit_rechnung",
        "finance_mahnstufen_audit",
        ["rechnungsnr", "tenant_id"],
        schema="domain_finance",
    )


def downgrade() -> None:
    op.drop_table("finance_mahnstufen_audit", schema="domain_finance")
    op.drop_table("finance_ratenzahlungsraten", schema="domain_finance")
    op.drop_table("finance_ratenzahlungsplaene", schema="domain_finance")
    op.drop_table("finance_sepa_batches", schema="domain_finance")
    op.drop_table("finance_sepa_mandate", schema="domain_finance")
